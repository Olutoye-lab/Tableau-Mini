import pandas as pd
from sqlalchemy import create_engine
from sse_manager import event_manager
from io import BytesIO, StringIO

class BridgeIngestor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.supported_extensions = ['.csv', '.xlsx', '.json']

    async def ingest(self, data_or_conn_string, limit=1, user_table_name=" ", dataType="csv"):
        """
        Main entry point. Detects source type and routes to the correct loader.
        Returns: A normalized Pandas DataFrame.
        """
        await event_manager.publish(self.user_id, event_type="normal", data="Ingestion")
        # Check if it's a SQL Connection String (simplistic check)
        if dataType == "string":
            print(f"--> Detecting SQL Connection...")
            return self._load_sql(data_or_conn_string, user_table_name, limit)
        

        if dataType == 'csv':
            print(f"--> Detecting CSV File...")
            return self._load_csv(data_or_conn_string)
        elif dataType == 'xlsx':
            print(f"--> Detecting Excel File...")
            return self._load_excel(data_or_conn_string)
        elif dataType == 'json':
            print(f"--> Detecting JSON File...")
            return self._load_json(data_or_conn_string)
        else:
            raise ValueError(f"Unsupported source type: {dataType}")

    # --- Specific Loaders ---

    def _load_csv(self, csv_data):
        # 'low_memory=False' helps with mixed types in large files (common in dirty data)
        return pd.read_csv(StringIO(csv_data), low_memory=False)

    def _load_excel(self, excel_data):
        # Reads the first sheet by default. 
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
        