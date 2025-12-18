from SemanticCore.agentforce_setup import call_agent
from sse_manager import event_manager
import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()

class EntityResolver:
    def __init__(self, user_id):
        """
        Initializes the entity resolver which resolves row incosistencies 
        """
        self.user_id = user_id
        self.resolution_cache = {} # "Memory" to avoid re-resolving known entities

    async def resolve(self, series: pd.Series) -> pd.Series:
        """
        Resolves a dirty column to standard entities efficiently.
        """
        await event_manager.publish(self.user_id, event_type="normal", data="Entity Resolution")

        # 1. Input Validation
        if series.empty:
            return series
            
        # 2. Optimization: Extract only UNIQUE values
        # We drop NA because we don't pay AI to clean nulls.
        unique_dirty_values = series.dropna().unique().tolist()
        
        # 3. Check Cache (Don't resolve what we already know)
        unknown_values = [
            val for val in unique_dirty_values 
            if val not in self.resolution_cache
        ]

        prompt = f"""
        Identify and merge entity name variants across datasets that refer to the same real-world entity (e.g., “IBM”, “I.B.M.”, “International Business Machines”).

        Input

        One or more datasets containing entity names with variations due to abbreviations, punctuation, casing, or legal suffixes.

        Task

        Normalize names (case, punctuation, common suffixes).

        Detect duplicates using string, acronym, and semantic similarity.

        Group names referring to the same entity.

        Choose a canonical name (most common or clearest).

        Output

        Return a dictionary mapping canonical names to their variants.

        {
        "IBM": [
            "International Business Machines",
            "I.B.M.",
            "International Business Machines Corp",
            "International Business Machines Corporation"
            ],
        "Google": [
            "Google Inc.",
            "Google LLC",
            "Alphabet Google"
            ]
        }


        Constraints
        Ensure all names are matched

        Preserve original name strings.

        INPUT:
        {json.dumps(unknown_values)}
        """
        # 4. Batch Process via AI (The Arbitrary Call)
        if unknown_values:
            print(f"⚙️ Entity Resolver: Sending {len(unknown_values)} unique items to AI...")
            
            try:
                agent_name = os.getenv("RESOLVER_AGENT_NAME")
                cleaned_results = call_agent(prompt, agent_name)
                
                # Validation: Ensure input length matches output length
                if len(cleaned_results) != len(unknown_values):
                    raise ValueError("AI function returned different number of items than provided.")
                
                # 5. Update Cache
                new_map = dict(zip(unknown_values, cleaned_results))
                self.resolution_cache.update(new_map)
                
            except Exception as e:
                print(f"⚠️ AI Resolution Failed: {e}")
                # Fallback: Return original values if AI fails
                return series

        # 6. Apply Mapping to the full dataset (Vectorized Map)
        # Using .get to handle any NaNs or unexpected values gracefully
        return series.map(lambda x: self.resolution_cache.get(x, x))