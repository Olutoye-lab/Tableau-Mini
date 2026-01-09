# Use a pipeline as a high-level helper
import pandas as pd
import uuid

class WeightedConfidenceCalculator:
    def __init__(self, user_id, df: pd.DataFrame, weights: dict):
        """
        df: The dataframe to check.
        weights: A dictionary defining importance. 
                 e.g., {'Revenue': 3.0, 'City': 1.0, 'Comments': 0.5}
                 Default weight is 1.0 if not specified.
        """
        self.user_id = user_id
        self.df = df
        self.weights = weights
        self.null_score = [0, 0] # [7, 10] means 7/10 columns has at least 1 null value
        self.event_data = {} # For User SSE events
        self.report_log = [] # For dashboard reporting
        
        # Initialize a dictionary to track the raw score of each column (0-100)
        # e.g., {'Revenue': 100, 'City': 100, 'Comments': 100}
        self.column_scores = {col: 100.0 for col in df.columns}

    def check_nulls(self, column: str):
        """
        Rule: Deduct 1 point from THIS COLUMN'S score for every 1% of nulls.
        """
        self.null_score[1] += 1

        if column not in self.df.columns:
            return

        total = len(self.df)
        null_count = self.df[column].isnull().sum()
        
        if null_count > 0:
            self.null_score[0] += 1
            percent_null = (null_count / total) * 100
            # Apply penalty only to this specific column
            self.column_scores[column] -= percent_null
            self.column_scores[column] = max(0, self.column_scores[column]) # Cap at 0
            
            self.report_log.append(f"[{column}] Penalized {percent_null:.1f} pts for nulls.")

    def check_uniqueness(self, column: str, is_primary_key: bool = False):
        """
        Only penalizes duplicates if the column is SUPPOSED to be unique (Primary Key).
        """
        if column not in self.df.columns:
            return

        # If it's just a normal column (like Region or Customer_ID), skip the check.
        if not is_primary_key:
            self.report_log.append({
                "id": str(uuid.uuid4()),
                "column": column,
                "type": "Skipped Uniquness check",
                "message": f"[{column}] Skipped uniqueness check (Duplicates allowed).",
                "status": "info"
                })
            return 

        # If it IS the Primary Key, duplicates are a disaster.
        if not self.df[column].is_unique:
            self.column_scores[column] = 0  # CRITICAL FAILURE
            self.report_log.append({
                "id": str(uuid.uuid4()),
                "column": column,
                "type": "Uniqueness Failure",
                "message": f"[{column}] FATAL ERROR: Primary Key has duplicates.",
                "status": "critical"
                })

    def calculate_weighted_score(self):
        """
        Aggregates individual column scores into one final 'Business Trust Score'.
        Formula: Sum(Score * Weight) / Sum(Weights)
        """
        total_weighted_score = 0
        total_weight = 0
        self.event_data["fields"] = []


        print(f"{'Column':<15} | {'Raw Score':<10} | {'Weight':<8} | {'Contribution'}")
        print("-" * 55)

        formated_column_scores = []

        for col, raw_score in self.column_scores.items():
            # Get weight (default to 1.0 if not defined)
            weight = self.weights.get(col, 1.0)
            
            # Math
            weighted_val = raw_score * weight
            total_weighted_score += weighted_val
            total_weight += weight
            
            col_score = {"name": col, "score": round(float(raw_score), 2)}

            formated_column_scores.append(col_score)

            self.event_data["fields"].append(col_score)
            
            print(f"{col:<15} | {raw_score:<10.1f} | {weight:<8} | {weighted_val:.1f}")

        
        if total_weight <= 40:
            self.event_data["text"] = "It seems you data doesn't meet the quality threshold, please check the results and refrain from using this on heavy data analysis."
        elif 40 < total_weight < 70:
            self.event_data["text"] = "Your data passes basic quality checks. However there maybe hidden logical issues within within your dataset, please check the results for further information."
        else:
            self.event_data["text"] = "Your dataset passes most quality checks and it optimal for data analysis."

        final_score = total_weighted_score / total_weight

        # Avoid division by zero
        if total_weight == 0:
            self.event_data["score"] = 0,
            return self.event_data
                
        self.event_data["score"] = round(float(final_score), 2)
        return self.event_data, self.report_log, formated_column_scores, self.null_score, final_score, 

