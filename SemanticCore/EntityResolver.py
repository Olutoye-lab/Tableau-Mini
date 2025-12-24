from agent import call_salesforce_agent
from sse_manager import event_manager
import pandas as pd
import json
from dotenv import load_dotenv
import os
import re

load_dotenv()

class EntityResolver:
    def __init__(self, user_id):
        """
        Initializes the entity resolver which resolves row incosistencies 
        """
        self.user_id = user_id
        self.resolution_cache = {} # "Memory" to avoid re-resolving known entities

    def resolve(self, series: pd.Series) -> pd.Series:
        """
        Resolves a dirty column to standard entities efficiently.
        """
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

        example = '{ "IBM": [ "IBM corp", "I.B.M.", "International Business Machines", ] }'
        empty_dict = "{}"
        prompt = f"""
        Please Identify and merge entity name variants across datasets that refer to the same real-world entity (e.g., “IBM”, “I.B.M.”, “International Business Machines”).
        If no actions can be performed, please return an empty dict e.g. {empty_dict}
        INPUT:
        {json.dumps(unknown_values)}

        OUTPUT: 
        Return a dictionary mapping canonical names to their variants {example}
        Or an Empty dict {empty_dict}
        """
        # 4. Batch Process via AI (The Arbitrary Call)
        if unknown_values:
            print(f"⚙️ Entity Resolver: Sending {len(unknown_values)} unique items to AI...")
            
            try:
                agent_id = os.getenv("ENTITY_AGENT_ID") or ""
                response = call_salesforce_agent(message=prompt, agent_id=agent_id)

                print(response)

                match = re.search(r'\{.*?\}', response, flags=re.DOTALL)

                if match:
                    string = match.group(0)
                else:
                    string = empty_dict

                results = json.loads(string)

                formatted_results = {}  
                for key, dirty_values in results.items():
                    # key: mapped value (str)
                    # dirty_values: some original values (list)
                    formatted_results.update(dict(map(lambda x: (x, key), dirty_values)))
            
                self.resolution_cache.update(formatted_results)
                
            except Exception as e:
                raise ValueError (f"⚠️ AI Resolution Failed: {e}")


        # 6. Apply Mapping to the full dataset (Vectorized Map)
        # Using .get to handle any NaNs or unexpected values gracefully
        return series.map(lambda x: self.resolution_cache.get(x, x))