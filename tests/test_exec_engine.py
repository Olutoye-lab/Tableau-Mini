# from ExecutionEngine.ConfidenceAnalysis import WeightedConfidenceCalculator

# import pandas as pd

# def test_weighted_calculator():
#     # --- SCENARIO: The "Critical Failure" that doesn't matter ---
#     # Imagine a dataset where 'Revenue' is perfect, but 'Comments' is messy.
#     # A standard average would drop the score heavily. 
#     # A weighted average preserves the score because 'Revenue' matters more.

#     # 1. Setup Data
#     data = {
#         'Transaction_ID': [1, 2, 3, 4, 5],      # Perfect
#         'Revenue': [100, 200, 300, 400, 500],   # Perfect
#         'Comments': [None, None, None, None, 'OK'] # 80% Nulls (Messy!)
#     }
#     df = pd.DataFrame(data)

#     # 2. Define Business Priorities (The "Impact" Layer)
#     business_weights = {
#         'Transaction_ID': 2.0,  # Important
#         'Revenue': 3.0,         # Critical
#         'Comments': 0.5         # Low Priority
#     }

#     # 3. Run Checks
#     user_id = ""
#     calculator = WeightedConfidenceCalculator(user_id, df, business_weights)

#     # Apply checks to relevant columns
#     calculator.check_uniqueness('Transaction_ID') # Passes
#     calculator.check_nulls('Revenue')             # Passes
#     calculator.check_nulls('Comments')            # Fails badly (-80 pts)

#     # 4. Calculate
#     print("\n--- detailed scoring breakdown ---")
#     report_data = calculator.calculate_weighted_score()

#     print("\n" + "="*30)
#     print(f"FINAL DATA: {report_data}")
#     print("="*30)
#     print("Score", report_data["score"])
