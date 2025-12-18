# Use a pipeline as a high-level helper
import pandas as pd
from sse_manager import event_manager

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
        
        # Initialize a dictionary to track the raw score of each column (0-100)
        # e.g., {'Revenue': 100, 'City': 100, 'Comments': 100}
        self.column_scores = {col: 100.0 for col in df.columns}
        self.report_log = []

    async def check_nulls(self, column: str):
        """
        Rule: Deduct 1 point from THIS COLUMN'S score for every 1% of nulls.
        """
        await event_manager.publish(self.user_id, event_type="normal", data="Confidence Analysis")

        if column not in self.df.columns:
            return

        total = len(self.df)
        null_count = self.df[column].isnull().sum()
        
        if null_count > 0:
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
            self.report_log.append(f"[{column}] Skipped uniqueness check (Duplicates allowed).")
            return

        # If it IS the Primary Key, duplicates are a disaster.
        if not self.df[column].is_unique:
            self.column_scores[column] = 0  # CRITICAL FAILURE
            self.report_log.append(f"[{column}] FATAL ERROR: Primary Key has duplicates.")

    def calculate_weighted_score(self):
        """
        Aggregates individual column scores into one final 'Business Trust Score'.
        Formula: Sum(Score * Weight) / Sum(Weights)
        """
        total_weighted_score = 0
        total_weight = 0

        print(f"{'Column':<15} | {'Raw Score':<10} | {'Weight':<8} | {'Contribution'}")
        print("-" * 55)

        for col, raw_score in self.column_scores.items():
            # Get weight (default to 1.0 if not defined)
            weight = self.weights.get(col, 1.0)
            
            # Math
            weighted_val = raw_score * weight
            total_weighted_score += weighted_val
            total_weight += weight
            
            print(f"{col:<15} | {raw_score:<10.1f} | {weight:<8} | {weighted_val:.1f}")

        # Avoid division by zero
        if total_weight == 0:
            return 0

        final_score = total_weighted_score / total_weight
        return round(final_score, 2)

