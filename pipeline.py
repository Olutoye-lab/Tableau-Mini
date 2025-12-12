from IngestionLayer.BridgeIngestor import BridgeIngestor
from IngestionLayer.MetadataScanner import MetadataScanner
from sse_manager import event_manager

import json


async def run_pipline(payload, user_id):
        
    credentials = payload["credentials"]
    dataType = payload["dataType"]

    # Data or string is a list of data or Connection string
    data_or_string = payload["data"]
    limit = payload["limit"]
    table_name = payload["table_name"]
    department = payload["department"]
    user_input = payload["user_input"]


    table_data = await ingest_data(user_id, dataType, data_or_string, limit, table_name)

    for table_profile, data in table_data:
        pass



async def ingest_data(user_id, dataType, data_or_string, limit, table_name):
    data_ingestor = BridgeIngestor()

    # table is a list of data frames, either 1 or multiple

    if "://" in dataType:
        tables = [data_ingestor.ingest(data_or_conn_string=data_or_string, limit=limit, user_table_name=table_name, dataType=dataType)]
    else:
        tables = []
        for data in data_or_string:
            tables.append(data_ingestor.ingest(data_or_conn_string=data))

    await event_manager.publish(user_id, event_type="normal", data="Finished data ingestion")


    # --- Meta data scanner ---

    column_profiles = []
    scanner = MetadataScanner()

    for table in tables:
        column_profiles.append(scanner.scan(table))

    await event_manager.publish(user_id, event_type="normal", data="Finished Metadata Scanning")


    return dict(zip(column_profiles, tables))

    