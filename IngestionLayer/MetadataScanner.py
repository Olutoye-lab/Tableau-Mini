import pandas as pd
import json
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
        profile = {}
        event_data = {}

        for col in df.columns:
            # 1. Global Stats (Calculate on FULL data for accuracy)
            total_rows = len(df)
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            
            # Calculate Ratios for the Logic Engine
            unique_ratio = unique_count / total_rows if total_rows > 0 else 0
            null_ratio = null_count / total_rows if total_rows > 0 else 0
            
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
        Determines the specific Inferred Type and Semantic Tag based on 
        Security, Structure, and Content analysis.
        """
        if series.empty:
            return "Unknown", "Empty"

        # --- LEVEL 1: SECURITY CHECKS (Highest Priority) ---
        # Check for Credit Card Numbers (Simple Regex for 16 digits)
        if series.astype(str).str.contains(r'^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$').any():
            return "String", "PII_Financial_Sensitive"

        # Check for Emails
        if series.astype(str).str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$').any():
            return "String", "PII_Contact_Email"

        # Check for US Social Security Numbers
        if series.astype(str).str.contains(r'^\d{3}-\d{2}-\d{4}$').any():
            return "String", "PII_Government_ID"

        # --- LEVEL 2: STRUCTURAL CHECKS (Relational Logic) ---
        # Check for Boolean Flags (Low Cardinality + Specific Values)
        if series.nunique() <= 2:
             sample_values = set(series.astype(str).unique())
             # Clean up the set to ensure we match correctly
             clean_values = {v.lower() for v in sample_values}
             if clean_values.issubset({'y', 'n', 'true', 'false', '0', '1', 't', 'f'}):
                 return "Boolean", "Logic_Flag"

        # Check for Primary Keys (100% Unique, No Nulls)
        # Note: We rely on the GLOBAL ratios passed in, not the sample
        if unique_ratio == 1.0 and null_ratio == 0.0:
            if pd.api.types.is_integer_dtype(series):
                return "Integer", "Primary_Key"
            # Heuristic: Long unique strings (avg len > 10) are usually UUIDs
            elif series.astype(str).str.len().mean() > 8: 
                return "String", "UUID_Key"

        # --- LEVEL 3: CONTENT CHECKS (Standard Types) ---
        # Check for Dates
        try:
            series.apply(lambda x: parse(x) if pd.notna(x) else pd.NaT)
            return "Datetime", "Time_Dimension"
        except:
            pass

        # Check for Numeric Measures
        try:
            # Clean currency symbols before checking
            clean_series = series.astype(str).str.replace(r'[$,]', '', regex=True)
            pd.to_numeric(clean_series)
            return "Numeric", "Measure"
        except:
            pass

        # --- FALLBACK ---
        return "String", "Categorical_Dimension"