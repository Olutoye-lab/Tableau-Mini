from IngestionLayer.BridgeIngestor import BridgeIngestor
from IngestionLayer.MetadataScanner import MetadataScanner
from SemanticCore.IntentDecoder import IntentDecoder
from SemanticCore.SemanticMapper import SemanticMapper
from SemanticCore.EntityResolver import EntityResolver

from .sse_manager import event_manager
import pandas as pd
import asyncio


async def run_pipline(payload, user_id):
        
    credentials = payload["credentials"]
    dataType = payload["dataType"]

    # Data or string is a list of data or Connection string
    data_or_string = payload["data"]
    limit = payload["limit"]
    table_name = payload["table_name"]
    user_input = payload["user_input"]


    table_data = await ingest_data(user_id, dataType, data_or_string, limit, table_name)

    cleaned_df = await run_intelligence_pipeline(table_data=table_data, user_input=user_input)




async def run_intelligence_pipeline(table_data, user_input):
    decoder = IntentDecoder()

    # ----- INTENT DECODER ---- 
    for table_profile, data in table_data:
        # table_profile: metadata on the columns
        # data: Dataframe of full data

        ontology = decoder.decode_intent(user_prompt=user_input, metadata_profile=table_profile)
        # finance, sales or human resources

        mapper = SemanticMapper()
        data_resolver = EntityResolver()

        mapper.precompute_ontology(ontology_json=ontology)

        # Map ontology vector embeddings

        ### ADD WEIGTHS TO ONTOLOGY


        updated_col_mappings = await  mapper.map_columns(raw_input=data)
        updated_col_names = list(updated_col_mappings.keys())

        updated_data_dict = {}

        col_index = 0
        for column_name, column_data in data.iteritems():
            updated_data_dict[updated_col_names[col_index]] = data_resolver.resolve(series=pd.Series(column_data))

        updated_df = pd.DataFrame(updated_data_dict)

        return updated_df



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

    