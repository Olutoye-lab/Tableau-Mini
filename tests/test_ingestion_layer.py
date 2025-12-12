from IngestionLayer.BridgeIngestor import BridgeIngestor
from IngestionLayer.MetadataScanner import MetadataScanner

from .utils import build_test_payload
import asyncio

async def run_ingestion_test(mode="normal"): 

    payload = build_test_payload("csv", file_name='sample_data/normal_data/finance.csv')

    # --- Data Ingestor ---

    print("----- DATA PARSED -----")
    print(payload["data_or_string"][0:100])
    

    data_ingestor = BridgeIngestor()

    # table is a list of data frames, either 1 or multiple

    if payload["dataType"] == "string":
        tables = [data_ingestor.ingest(data_or_conn_string=payload["data_or_string"], limit=payload["limit"], user_table_name=payload["table_name"])]
    else:
        tables = []
        for data in payload["data_or_string"]:
            tables.append(data_ingestor.ingest(data_or_conn_string=data))
            print("Table finised")

    print(tables)
    print("----- INGESTION FINISHED -----")


    # --- Meta data scanner ---

    print("----- SCANNING METADATA -----")

    column_profiles = []

    for table in tables:
        scanner = MetadataScanner()
        column_profiles.append(scanner.scan(table))

    print(column_profiles)


    return True

def test_run_ingestion_test():
    assert asyncio.run(run_ingestion_test()) == True