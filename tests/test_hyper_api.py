import pytest
import pandas as pd
import os
from datetime import datetime

# --- IMPORT YOUR CLASS HERE ---
from ExecutionEngine.HyperAPI import HyperParquetIngestor 
from ExecutionEngine.PublishTableau import TableauCloudPublisher

# ==========================================
# 1. FIXTURES
# ==========================================

@pytest.fixture
def hyper_file_path(tmp_path):
    """
    Uses PyTest's native 'tmp_path' fixture. 
    It creates a unique temporary directory for each test and 
    automatically deletes it after the test finishes.
    """
    # Create a full path string inside the temp directory
    return str(tmp_path / "test_output.hyper")

@pytest.fixture
def sample_df():
    """Creates a standard dataframe for testing."""
    return pd.DataFrame({
        'Transaction_ID': [1, 2, 3],
        'Revenue': [100.50, 200.00, 300.25],
        'Is_Valid': [True, False, True],
        'Category': ['A', 'B', 'A']
    })

# ==========================================
# 2. THE TESTS
# ==========================================
# def test_file_creation(hyper_file_path, sample_df):
#     """
#     Scenario: Does the ingestor physically create the file?
#     """
#     ingestor = HyperParquetIngestor(hyper_file_path)
#     ingestor.generate_file(sample_df, "Test_Table")
    
#     assert os.path.exists(hyper_file_path), "Hyper file was not created on disk."

# def test_data_integrity(hyper_file_path, sample_df):
#     """
#     Scenario: Open the generated Hyper file and check if the math matches.
#     """
#     ingestor = HyperParquetIngestor(hyper_file_path)
#     ingestor.generate_file(sample_df, "Test_Table")

#     # Connect to the result using Hyper API to verify
#     with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
#         with Connection(endpoint=hyper.endpoint, database=hyper_file_path) as connection:
            
#             # Check Row Count
#             row_count = connection.execute_scalar_query(
#                 'SELECT COUNT(*) FROM "Extract"."Test_Table"'
#             )
#             assert row_count == 3, f"Expected 3 rows, got {row_count}"

#             # Check Revenue Sum
#             revenue = connection.execute_scalar_query(
#                 'SELECT SUM("Revenue") FROM "Extract"."Test_Table"'
#             )
#             # pytest.approx handles floating point issues
#             assert revenue == pytest.approx(600.75), f"Revenue sum mismatch. Got {revenue}"

# def test_empty_dataframe(hyper_file_path):
#     """
#     Scenario: System should not crash on empty data.
#     """
#     # Explicitly set dtype to ensure the schema generator knows what to do
#     empty_df = pd.DataFrame({
#         'ColA': pd.Series(dtype='int'), 
#         'ColB': pd.Series(dtype='object')
#     })
    
#     ingestor = HyperParquetIngestor(hyper_file_path)
    
#     try:
#         ingestor.generate_file(empty_df, "Empty_Table")
#     except Exception as e:
#         pytest.fail(f"Ingestor crashed on empty DataFrame: {e}")
    
#     assert os.path.exists(hyper_file_path)

#     # Optional: Verify table exists but has 0 rows
#     with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
#         with Connection(endpoint=hyper.endpoint, database=hyper_file_path) as connection:
#             count = connection.execute_scalar_query('SELECT COUNT(*) FROM "Extract"."Empty_Table"')
#             assert count == 0

# def test_schema_mapping(hyper_file_path):
#     """
#     Scenario: Ensure Booleans stay Booleans using the Catalog API.
#     """
#     df_bool = pd.DataFrame({'Is_Active': [True, False]})
#     ingestor = HyperParquetIngestor(hyper_file_path)
#     ingestor.generate_file(df_bool, "Bool_Test")

#     with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
#         with Connection(endpoint=hyper.endpoint, database=hyper_file_path) as connection:
            
#             # USE CATALOG API (More robust than raw SQL on system tables)
#             table_def = connection.catalog.get_table_definition(TableName("Extract", "Bool_Test"))
            
#             # Find the column
#             col = next(c for c in table_def.columns if c.name.unescaped == "Is_Active")
            
#             # Check the SqlType
#             assert 'BOOL' in str(col.type).upper(), f"Column mapped incorrectly. Got: {col.type}"


def test_live_publish_to_cloud(hyper_file_path, sample_df):
    """
    REAL WORLD TEST: Generates a file and attempts to actually upload it 
    to Tableau Cloud. Requires valid ENV variables.
    """
    
    # 1. Load Credentials from Environment
    #    Make sure these are set in your terminal or .env file before running
    server_url = os.getenv("TB_SERVER_URL")
    site_name = os.getenv("TB_SITE_NAME")
    token = os.getenv("TB_TOKEN")
    token_name = os.getenv("TB_TOKEN_NAME")
    
    # Target specific sandbox area for safety
    target_project = "Test_Project"  # OR: os.getenv("TABLEAU_TEST_PROJECT")
    target_datasource = "Test_Datasource/" + datetime.now().strftime("%H:%M:%S")

    # Fail fast if credentials are missing
    if not all([server_url, site_name, token, token_name]):
        pytest.skip("Skipping live test: Missing environment variables.")

    # 2. Funnel: Generate the real Hyper file
    print(f"\n[1/3] Generating temp file at: {hyper_file_path}")
    ingestor = HyperParquetIngestor(hyper_file_path)
    ingestor.generate_file(sample_df, "Integration_Test_Table")
    
    assert os.path.exists(hyper_file_path), "Failed to generate temp file."

    # 3. Initialize Real Publisher
    print(f"[2/3] Connecting to real server: {server_url}")
    publisher = TableauCloudPublisher(
        server_url=server_url, 
        site_name=site_name, 
        token=token,
        token_name=token_name
    )

    # 4. Execute Publish
    #    If this fails, it will raise an Exception and fail the test automatically.
    print(f"[3/3] Attempting upload to Project: '{target_project}'...")
    
    try:
        publisher.publish(
            file_path=hyper_file_path, 
            project_name=target_project, 
            datasource_name=target_datasource,
            certify=True
        )
    except Exception as e:
        pytest.fail(f"Live Publish Failed: {e}")

    print("\n✅ Live publish test completed successfully.")