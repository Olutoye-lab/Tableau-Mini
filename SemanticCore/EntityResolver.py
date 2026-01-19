from agent import call_salesforce_agent
import pandas as pd
import json
from dotenv import load_dotenv
import os
import re
import uuid

load_dotenv()

class EntityResolver:
    def __init__(self, user_id):
        """
        Initializes the entity resolver which resolves row incosistencies 
        """
        self.user_id = user_id
        self.report_log = []
        self.resolution_cache = {} # "Memory" to avoid re-resolving known entities

    def resolve(self, series: pd.Series, col_name: str) -> pd.Series:
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
        An Entity is defined as a string which can be mapped to other variants (e.g. Pend, pending, pnding -> Pending). This does not include strings which are meant to be unqiue (e.g. names like Mike S & Mario S)
        If no actions can be performed, please return an empty dict e.g. {empty_dict}
        INPUT:
        {json.dumps(unknown_values)}

        OUTPUT: 
        Return a dictionary mapping canonical names to their variants {example}
        Or an Empty dict {empty_dict}
        """
        # 4. Batch Process via SalesForce models
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
                    self.report_log.append({
                        "id": str(uuid.uuid4()),
                        "column": col_name,
                        "type": "Inconsistent Cell Namming",
                        "message": f"Cells {", ".join(dirty_values)} ' were semantically mapped to {key}. Please validate with your team on consitent naming conventions!! ",
                        "status": "critical"
                    })

                    formatted_results.update(dict(map(lambda x: (x, key), dirty_values)))
            
                self.resolution_cache.update(formatted_results)
                
            except Exception as e:
                raise ValueError (f"⚠️ AI Resolution Failed: {e}")


        # 6. Apply Mapping to the full dataset (Vectorized Map)
        # Using .get to handle any NaNs or unexpected values gracefully
        return series.map(lambda x: self.resolution_cache.get(x, x))

    def resolve_date(self, series, column) -> pd.Series:
        """
        Resolves inconsistent format between dates
        """

        series = pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")
        series = series.dt.strftime("%Y-%m-%d")

        self.report_log.append({
            "id": str(uuid.uuid4()),
            "column": column,
            "type": "Inconsistent datetime",
            "message": f"Column '{column}', has found to have an inconsistent date schema. It has been corrected. (Y-M-D)'.",
            "status": "warning"
        })

        return series
    
    def resolve_headers(self, df):
        """
        Resolves datasets for irrelevant headers

        Input: 
        df: pd.Dataframe -> A pandas dataframe
        """

        example = '["Mood", "Lamp_shade", "Pencil_thickness"]'
        empty_list = "[]"
        prompt=f"""
        From the provided dataset identify the column header(s) which may be proffesionally irrelevant to every other header (e.g. Revenue, Customer_ID, Shoe_size) -> ["Shoe_size"]
        If no headers are identified, please return an empty list e.g. {empty_list}
        
        INPUT
        {df.head(n=5)}

        OUTPUT: 
        Return a list of irrelevant headers {example}
        Or an Empty list {empty_list}
        """

        agent_id = os.getenv("COLUMN_AGENT_ID") or ""
        response = call_salesforce_agent(message=prompt, agent_id=agent_id)

        print(response)
        
        match = re.search(r'\[.*?\]', response, flags=re.DOTALL)

        if match:
            string = match.group(0)
        else:
            string = empty_list
        
        print("string", string)

        headers = string.removeprefix("[").removesuffix("]").replace('"', "").split(", ")

        print("Irrelevant headers", headers)
        print(type(headers))

        for header in headers:
            self.report_log.append({
                "id": str(uuid.uuid4()),
                "column": header,
                "type": "Potentially Irrelevant Headers",
                "message": f"Column '{header}', has been flagged as irrelevant to the dataset context. Please validate this for future use.",
                "status": "critical"
            })

    def get_logs(self):
        return self.report_log