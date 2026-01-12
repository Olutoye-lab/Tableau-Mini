# Use a pipeline as a high-level helper
import pandas as pd
import uuid

class WeightedConfidenceCalculator:
    def __init__(self, user_id, df: pd.DataFrame, weights: dict, deducted_points: dict):
        """
        df: The dataframe to check.
        weights: A dictionary defining importance. 
                 e.g., {'Revenue': 3.0, 'City': 1.0, 'Comments': 0.5}
                 Default weight is 1.0 if not specified.
        """
        self.user_id = user_id
        self.df = df
        self.weights = weights
        self.deducted_points = deducted_points
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
        
        for log in self.report_log:
            print("-------------------------------------------")
            print("LOG", log)
            if (log["status"] == "critical"):
                print(f"Log {log["column"]} = -20 ")
                self.deducted_points[log["column"]] += 20
            elif log["status"] == "warning":
                print(f"Log {log["column"]} = -10 ")
                self.deducted_points[log["column"]] += 10
            elif log["status"] == "info":
                print(f"Log {log["column"]} = -0 ")
                self.deducted_points[log["column"]] += 0

        print("TOTAL DEDUCTED", self.deducted_points)

        print(f"{'Column':<15} | {'Raw Score':<10} | {'Weight':<8} | {'Contribution'}")
        print("-" * 55)

        formated_column_scores = []

        for col, raw_score in self.column_scores.items():

            print(f"COLUMN: {col}. Deducted score {self.deducted_points[col]}")

            if (self.deducted_points[col] >= 100):
                raw_score = 0
            else:
                raw_score = raw_score - self.deducted_points[col]
            

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

        
        final_score = total_weighted_score / total_weight

        final_score = round(float(final_score), 2)

        if final_score <= 40:
            self.event_data["text"] = "It seems you data doesn't meet the quality threshold, please check the results and refrain from using this on heavy data analysis."
        elif 40 < final_score < 90:
            self.event_data["text"] = "Your data passes basic quality checks. However there maybe hidden logical issues within within your dataset, please check the results for further information."
        else:
            self.event_data["text"] = "Your dataset passes most quality checks and it optimal for data analysis."


        # Avoid division by zero
        if total_weight == 0:
            self.event_data["score"] = 0,
            return self.event_data
                
        self.event_data["score"] = final_score
        return self.event_data, self.report_log, formated_column_scores, self.null_score, final_score, 

