from IngestionLayer.BridgeIngestor import BridgeIngestor
from IngestionLayer.MetadataScanner import MetadataScanner
from SemanticCore.IntentDecoder import IntentDecoder
from SemanticCore.SemanticMapper import SemanticMapper
from SemanticCore.EntityResolver import EntityResolver
from ExecutionEngine.ConfidenceAnalysis import WeightedConfidenceCalculator
from ExecutionEngine.HyperAPI import HyperParquetIngestor
from ExecutionEngine.PublishTableau import TableauCloudPublisher

from sse_manager import event_manager
from salesforce_auth_manager import StorageManager
import pandas as pd
import json
import asyncio 
import tempfile
import random
from datetime import datetime


async def run_pipeline(payload, user_id):

    print(payload)
        
    token = payload["token"]
    token_name = payload["token_name"]
    server_url = payload["server_url"]
    site_name = payload["site_name"]
    dataType = payload["dataType"]
    data_or_string = payload["data"] # file text data or Postgress connection string
    limit=None
    table_name=None

    print("----------------------")
    print(data_or_string)
    print(dataType)
    print(token)
    print(token_name)


    if dataType.lower() == "string":
        limit = payload["limit"]
        table_name = payload["table_name"]

    table_data = await ingest_data(user_id, dataType, data_or_string, limit, table_name)

    print(table_data)

    cleaned_df, ontology, table_profile, semantic_core_logs = await run_intelligence_pipeline(user_id, table_data=table_data)

    print(cleaned_df)

    credentials = {
        "site_name": site_name,
        "server_url": server_url,
        "token": token,
        "token_name": token_name
    }

    await run_execution_engine(user_id, ontology, df=cleaned_df, table_profile=table_profile, credentials=credentials, total_logs=semantic_core_logs)

    return ""

async def run_execution_engine(user_id, ontology, df, table_profile, credentials, total_logs):

    weights = {}

    for items in ontology["required_fields"]:
        weights[items[0]] = items[1]

    calculator = WeightedConfidenceCalculator(user_id, df, weights)

    for col in df.columns:
        # Apply checks to relevant columns
        calculator.check_uniqueness(col, is_primary_key=table_profile[col]["is_likely_id"])
        null = calculator.check_nulls(col)

    report_data, logs, formated_column_scores, null_score, final_score = await asyncio.to_thread(calculator.calculate_weighted_score)
    
    metadata = {
        "column_scores": formated_column_scores,
        "null_score": null_score,
        "report_score": final_score
    }

    total_logs.extend(logs)

    print("Total logs", total_logs)

    report_name = str(random.randrange(0, 1000)).ljust(4, "0")

    await asyncio.to_thread(StorageManager.add_report, report_data=total_logs, user_id=user_id, report_name=f"Mini Report {report_name}", metadata=metadata)
    
    target_project = "Mini_Project"  # OR: os.getenv("TABLEAU_TEST_PROJECT")
    target_datasource = "Mini_Datasource/" + datetime.now().strftime("%H:%M:%S")

    with tempfile.TemporaryDirectory() as temp_dir:

        hyper_file_path = temp_dir + "/test_output.hyper"
        ingestor = HyperParquetIngestor(hyper_file_path=hyper_file_path, user_id=user_id)
        ingestor.generate_file(df, "Integration_Table")

        # 3. Initialize Real Publisher
        print(f"[2/3] Connecting to real server: {credentials["server_url"]}")
        publisher = TableauCloudPublisher(
            user_id=user_id,
            server_url=credentials["server_url"], 
            site_name=credentials["site_name"], 
            token=credentials["token"],
            token_name=credentials["token_name"]
        )

        # 4. Execute Publish
        #    If this fails, it will raise an Exception and fail the test automatically.
        print(f"[3/3] Attempting upload to Project: '{target_project}'...")
        
        try:
            await asyncio.to_thread(publisher.publish, 
                file_path=hyper_file_path, 
                project_name=target_project, 
                datasource_name=target_datasource,
                certify=True
            )

            event_data ={
                "id": 5,
                "title": "Results",
                "text": "Please view the main page for your results.",
                "report" : report_data
            }
            await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))
            
        except Exception as e:
            raise ValueError("Unable to publish to tableau", e)

        print("\n✅ Live publish test completed successfully.")

async def run_intelligence_pipeline(user_id, table_data):
    logs = []
    decoder = IntentDecoder(user_id)

    # ----- INTENT DECODER ---- 
    for table_profile, data in table_data:

        print("TABLE PROFILE", table_profile)
        # table_profile: metadata on the columns
        # data: Dataframe of full data

        ontology, event_data = await asyncio.to_thread(decoder.decode_intent, metadata_profile=table_profile)
        # finance, sales or human resources
        await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))


        mapper = SemanticMapper(user_id)
        data_resolver = EntityResolver(user_id)

        mapper.precompute_ontology(ontology_json=ontology)

        # Map ontology vector embeddings
        updated_col_mappings, event_data, semantic_logs = await asyncio.to_thread(mapper.map_columns, raw_input=data)
        logs.extend(semantic_logs)

        await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))

        updated_col_names = list(updated_col_mappings.keys())


        updated_data_dict = {}

        col_index = 0
        for column_name, column_data in data.items():

            if table_profile[column_name]["inferred_type"] == "String" and table_profile[column_name]["semantic_tag"] == "Categorical_Dimension":
                updated_data_dict[updated_col_names[col_index]], resolver_logs = await asyncio.to_thread(data_resolver.resolve, series=pd.Series(column_data), col_name=updated_col_names[col_index])
                logs.extend(resolver_logs)
            else:
                updated_data_dict[updated_col_names[col_index]] = column_data

            col_index += 1

        updated_df = pd.DataFrame(updated_data_dict)

        event_data ={
            "id": 4,
            "title": "Column Entity Resolution",
            "text": "This section resolves various inconsistencies inside columns from, null value, duplicate value sets Example: I.B.M & IBM corp -> resolve to -> I.B.M. Here are some updated table values",
            "table": updated_df.head().to_dict(orient="records")
        }

        await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))

        return updated_df, ontology, table_profile, logs
    return "", "", "", ""

async def ingest_data(user_id, dataType, data_or_string: str, limit, table_name):
    data_ingestor = BridgeIngestor(user_id)

    # table is a list of data frames, either 1 or multiple

    if "://" in dataType:
        table, event_data = await asyncio.to_thread(data_ingestor.ingest, data_or_string=data_or_string, limit=limit, user_table_name=table_name, dataType=dataType)
    else:
        table, event_data = await asyncio.to_thread(data_ingestor.ingest, data_or_string)

    await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))

    # --- Meta data scanner ---

    column_profiles = []
    scanner = MetadataScanner(user_id)

    profile, event_data = await asyncio.to_thread(scanner.scan, table)
    column_profiles.append(profile)

    await event_manager.publish(user_id, event_type="normal", data=json.dumps(event_data))

    return zip(column_profiles, [table])

    