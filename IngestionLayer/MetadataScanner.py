import pandas as pd
import numpy as np
from dateutil.parser import parse
from sse_manager import event_manager

class MetadataScanner:
    def __init__(self, user_id):
        self.user_id = user_id
        self.event_data = []
        self.data_count = 0


    def scan(self, df: pd.DataFrame):
        """
        Input: Raw Pandas DataFrame
        Output: A dictionary 'Profile' summarizing every column.
        """
        str_cols = df.select_dtypes(include=["object", "string"]).columns
        df[str_cols] = df[str_cols].fillna("null")

        num_cols = df.select_dtypes(include=["number"]).columns
        df[num_cols] = df[num_cols].fillna(0)

        print(df.head(10))

        profile = {}
        event_data = {}

        for col in df.columns:
            # 1. Global Stats (Calculate on FULL data for accuracy)
            total_rows = len(df)
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            
            # Calculate Ratios for the Logic Engine
            unique_ratio = float(unique_count / total_rows) if total_rows > 0 else 0
            null_ratio = float(null_count / total_rows) if total_rows > 0 else 0
            
            # 2. Sample the data for expensive checks (Regex/Parsing)
            # We use 'head(1000)' so we don't slow down on massive files
            sample = df[col].dropna().head(1000)
            
            # 3. Detect Inferred Type & Semantic Meaning
            # FIX: Pass the calculated ratios here!
            inferred_type, semantic_tag = self._determine_type_and_tag(sample, unique_ratio, null_ratio)
            
            profile[col] = {
                "raw_dtype": str(df[col].dtype),
                "inferred_type": inferred_type,
                "semantic_tag": semantic_tag,
                "stats": {
                    "completeness": round((1 - null_ratio) * 100, 2),
                    "uniqueness": round(unique_ratio * 100, 2)
                },
                "is_likely_id": unique_count == total_rows
            }

            pf_copy = profile[col]

            pf_copy.update({"completeness": pf_copy['stats']['completeness']})
            pf_copy.update({"uniqueness": pf_copy['stats']['uniqueness']})
            pf_copy.update({"column_value": col})
            del pf_copy["stats"]

            self.event_data.append(pf_copy)

            if self.data_count == 5:
                event_data ={
                    "id": 1,
                    "title": "Metadata Scan",
                    "text": "A current scan of the data provided has indicated various semantics data statistics.",
                    "table": self.event_data
                }

            self.data_count += 1
            
        return profile, event_data
    
    def _determine_type_and_tag(self, series, unique_ratio, null_ratio):
            """
            Optimized type inference using sampling and thresholds.
            """
            if series.empty:
                return "Unknown", "Empty"

            # --- PRE-CLEANING ---
            # 1. Replace literal "null" strings with actual NaN so they are dropped
            # This fixes the "unable to parse: null" error
            series_cleaned = series.replace(
                ['null', 'NULL', 'Null', 'nan', 'NaN'], np.nan
            )
            
            # 2. Create non-null sample
            sample_size = 1000
            series_dropped = series_cleaned.dropna()
            
            if len(series_dropped) > sample_size:
                sample = series_dropped.sample(n=sample_size, random_state=42)
            else:
                sample = series_dropped

            if len(sample) == 0:
                return "Unknown", "Empty"

            # Convert sample to string once for regex operations
            sample_str = sample.astype(str)

            # --- LEVEL 1: SECURITY CHECKS (Keep as is) ---
            if sample_str.str.contains(r'^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$').mean() > 0.1:
                return "String", "PII_Financial_Sensitive"
            if sample_str.str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$').mean() > 0.1:
                return "String", "PII_Contact_Email"

            # --- LEVEL 2: STRUCTURAL CHECKS (Keep as is) ---
            if series.nunique(dropna=True) <= 2:
                unique_vals = set(series_dropped.unique().astype(str))
                clean_values = {v.lower() for v in unique_vals}
                if clean_values.issubset({'y', 'n', 'true', 'false', '0', '1', 't', 'f', 'yes', 'no'}):
                    return "Boolean", "Logic_Flag"

            if unique_ratio == 1.0 and null_ratio == 0.0:
                if pd.api.types.is_integer_dtype(series):
                    return "Integer", "Primary_Key"
                elif sample_str.str.len().mean() > 20: 
                    return "String", "UUID_Key"

            # --- LEVEL 3: CONTENT CHECKS ---
            
            # 1. CHECK FOR NUMERICS (Integers & Floats)
            # Check native types first
            if pd.api.types.is_numeric_dtype(series):
                if pd.api.types.is_integer_dtype(series):
                    return "Integer", "Measure"
                else:
                    return "Decimal", "Measure"
            
            # Check string-encoded numerics
            try:
                clean_sample = sample_str.str.replace(r'[$,]', '', regex=True)
                converted_num = pd.to_numeric(clean_sample, errors='coerce')
                
                if converted_num.notna().mean() > 0.8:
                    valid_nums = converted_num.dropna()
                    if (valid_nums % 1 == 0).all():
                        return "Integer", "Measure"
                    else:
                        return "Decimal", "Measure"
            except:
                pass

            # 2. CHECK FOR DATES (Robust Version)
            try:
                # FIX 1: Use errors='coerce' to turn unparseable strings (like noise) into NaT
                # FIX 2: Use dayfirst=True for "17/02/25"
                # FIX 3: Use format='mixed' for "07-Nov-25" and "2025-07-20" together
                converted_date = pd.to_datetime(
                    sample, 
                    errors='coerce', 
                    dayfirst=True, 
                    format='mixed'
                )
                
                # Check success rate
                if converted_date.notna().mean() > 0.8: 
                    # Sanity check for "Fake Dates" (Numbers treated as timestamps)
                    valid_dates = converted_date[converted_date.notna()]
                    if valid_dates.dt.year.min() < 1980:
                        return "Integer", "Measure" 
                    
                    return "Datetime", "Time_Dimension"
            except:
                pass

            # --- FALLBACK ---
            return "String", "Categorical_Dimension"