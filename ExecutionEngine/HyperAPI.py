import os
import tempfile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from sse_manager import event_manager

from tableauhyperapi import (
    HyperProcess, Connection, Telemetry, CreateMode, 
    TableDefinition, SqlType, TableName, escape_string_literal,
    Nullability
)

class HyperParquetIngestor:
    def __init__(self, user_id, hyper_file_path: str):
        self.user_id = user_id
        self.hyper_path = hyper_file_path

    def _map_pandas_to_hyper_type(self, dtype) -> SqlType:
        if pd.api.types.is_integer_dtype(dtype):
            return SqlType.big_int()
        elif pd.api.types.is_float_dtype(dtype):
            return SqlType.double()
        elif pd.api.types.is_bool_dtype(dtype):
            return SqlType.bool()
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            # Check for timezone awareness could be added here
            return SqlType.timestamp() 
        else:
            return SqlType.text()

    async def generate_file(self, df: pd.DataFrame, table_name: str = "Extract"):
        await event_manager.publish(self.user_id, event_type="normal", data="Creating .hyper File")

        # Create a named temporary file that closes automatically but isn't deleted immediately
        # We need it to persist so Hyper can read it, then we delete it manually.
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            temp_parquet_path = tmp_file.name
            
        try:
            print(f"1. Converting to Parquet (Arrow Engine)...")

            # This prevents the "Parquet Null Type" error on empty object columns
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].empty:
                    df[col] = df[col].astype('string')

            table = pa.Table.from_pandas(df)
            pq.write_table(table, temp_parquet_path)

            print(f"2. Starting Hyper Process...")
            with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
                with Connection(endpoint=hyper.endpoint,
                                database=self.hyper_path,
                                create_mode=CreateMode.CREATE_AND_REPLACE) as connection:

                    # Define Schema
                    columns = []
                    for col_name, dtype in df.dtypes.items():
  
                        sql_type = self._map_pandas_to_hyper_type(dtype)
                        # Explicitly allowing NULLs is safer for Parquet ingestion
                        columns.append(TableDefinition.Column(str(col_name), sql_type, nullability=Nullability.NULLABLE))
                    
                    connection.catalog.create_schema_if_not_exists("Extract")
                    table_def = TableDefinition(TableName("Extract", table_name), columns)
                    connection.catalog.create_table(table_def)

                    print(f"3. Executing COPY FROM Parquet...")
                    copy_command = f"""
                    COPY {table_def.table_name} 
                    FROM {escape_string_literal(temp_parquet_path)}
                    WITH (FORMAT PARQUET)
                    """
                    
                    count = connection.execute_command(copy_command)
                    print(f"   Success! Ingested {count} rows.")

        finally:
            # This block always runs, even if the code above crashes
            if os.path.exists(temp_parquet_path):
                os.remove(temp_parquet_path)
                print("   Temporary artifacts cleaned up.")

        print(f"Done. File created: {self.hyper_path}")

# --- USAGE ---
# df = pd.DataFrame(...)
# ingestor = HyperParquetIngestor("Final_Output.hyper")
# ingestor.generate_file(df)