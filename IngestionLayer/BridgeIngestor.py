import pandas as pd
from sqlalchemy import create_engine
from sse_manager import event_manager
from io import BytesIO, StringIO
from typing import Optional, Any
import json


class BridgeIngestor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.supported_extensions = ['.csv', '.xlsx', '.json']

    def ingest(self, data_or_string, limit: Optional[int]=1, user_table_name: Optional[str]=" ", dataType="csv"):
        """
        Main entry point. Detects source type and routes to the correct loader.
        Returns: A normalized Pandas DataFrame.
        """
        # Check if it's a SQL Connection String (simplistic check)
        df = None
        if dataType == "string":
            print(f"--> Detecting SQL Connection...")
            df = self._load_sql(data_or_string, user_table_name, limit)

        elif dataType == 'csv':
            print(f"--> Detecting CSV File...")
            df = self._load_csv(data_or_string)
        elif dataType == 'xlsx':
            print(f"--> Detecting Excel File...")
            df = self._load_excel(data_or_string)
        elif dataType == 'json':
            print(f"--> Detecting JSON File...")
            df = self._load_json(data_or_string)
    
        
        if df is not None:
            str_cols = df.select_dtypes(include=["object", "string"]).columns
            df[str_cols] = df[str_cols].fillna("null")

            num_cols = df.select_dtypes(include=["number"]).columns
            df[num_cols] = df[num_cols].fillna(0)

            print(df.head(10))

            event_data: dict[str, Any] ={
                "id": 0,
                "title": "Ingestion Data",
                "text": "This is the initial process which ingests data from your source (either locally or through a connection string) into the pipeline",
                "table": df.head().to_dict(orient="records")
            }

            return df, event_data
        else:
            print("DF IS NONE!!")
            event_data: dict[str, Any] = {}
            return pd.DataFrame(), event_data

    # --- Specific Loaders ---

    def _load_csv(self, csv_data):
        # 'low_memory=False' helps with mixed types in large files (common in dirty data)
        if type(csv_data) == list:
            return pd.DataFrame(csv_data)
        else: 
            return pd.read_csv(StringIO(csv_data), low_memory=False)

    def _load_excel(self, excel_data):
        # Reads the first sheet by default. 
        if type(excel_data) == list:
            return pd.DataFrame(excel_data)
        else: 
            return pd.read_excel(BytesIO(excel_data), engine='openpyxl')

    def _load_json(self, json_data):
        # 'orient' depends on structure, but 'records' is common for API dumps
        if isinstance(json_data, list):
            df = pd.json_normalize(json_data)
        elif isinstance(json_data, dict):
            # If nested, extract the relevant part
            df = pd.json_normalize(json_data.get(json_data[0], []))
        else:
            raise ValueError("Unexpected JSON format")
        
        return df

    def _load_sql(self, connection_string, user_table_name, limit):
        # Connection string format: postgresql://user:password@localhost:5432/mydatabase
        engine = create_engine(connection_string)
        # Security Note: In production, limit this query or use chunks!
        # For the Bridge prototype, we grab the whole table or a specific view.
        # Ideally, pass a specific query, not just a table dump.
        get_tables_query = """SELECT table_schema, table_name
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE'
                        AND table_schema NOT IN ('pg_catalog', 'information_schema');
                        """
        tables_df = pd.read_sql(get_tables_query, engine)
        table_names = tables_df[:, 1]
        
        for name in table_names:
            if name.lower() == user_table_name.strip().lower():
                query = f"SELECT * FROM {name} LIMIT {limit}"
                return pd.read_sql(query, engine)
            else:
                # return an Error message prompting the user to choose a table, giving a list of tables
                pass
        