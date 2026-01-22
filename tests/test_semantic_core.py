# from SemanticCore.IntentDecoder import IntentDecoder
# from SemanticCore.SemanticMapper import SemanticMapper
# from SemanticCore.EntityResolver import EntityResolver

# import pandas as pd
# import numpy as np
# import pytest
# import asyncio

# table_data = pd.DataFrame()
# profile = [{'Employee_ID': {'raw_dtype': 'object', 'inferred_type': 'String', 'semantic_tag': 'Categorical_Dimension', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 100.0}, 'is_likely_id': True}, 'Name': {'raw_dtype': 'object', 'inferred_type': 'String', 'semantic_tag': 'UUID_Key', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 100.0}, 'is_likely_id': True}, 'Job_Title': {'raw_dtype': 'object', 'inferred_type': 'String', 'semantic_tag': 'Categorical_Dimension', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 9.0}, 'is_likely_id': False}, 'Sector_Focus': {'raw_dtype': 'object', 'inferred_type': 'String', 'semantic_tag': 'Categorical_Dimension', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 12.0}, 'is_likely_id': False}, 'Years_Experience': {'raw_dtype': 'int64', 'inferred_type': 'Numeric', 'semantic_tag': 'Measure', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 16.0}, 'is_likely_id': False}, 'Annual_Salary': {'raw_dtype': 'int64', 'inferred_type': 'Numeric', 'semantic_tag': 'Measure', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 94.0}, 'is_likely_id': False}, 'Performance_Rating': {'raw_dtype': 'float64', 'inferred_type': 'Numeric', 'semantic_tag': 'Measure', 'stats': {'completeness': np.float64(100.0), 'uniqueness': 16.0}, 'is_likely_id': False}}]
# prompt = "Please map analyse this data. And Return ONLY one of these three text. Human Resources, Sales or Finance"
# user_id = ""

# @pytest.mark.asyncio
# async def test_intent_decoder():
#     decoder = IntentDecoder(user_id)

#     # get onthology - Json
#     for metadata in profile:
#         ontology = await decoder.decode_intent(user_prompt=prompt, metadata_profile=metadata)

#         print("====================")
#         print(ontology)

#         assert True
    

# @pytest.mark.asyncio   
# def test_semantic_mapper():
#     # 1. Setup Ontology
#     finance_ontology = {
#         "required_fields": ["Transaction_Date", "Gross_Amount", "Vendor_Name", "Cost_Center"]
#     }

#     # 2. Init Mapper
#     mapper = SemanticMapper(threshold=0.6, user_id="")
#     mapper.precompute_ontology(finance_ontology)

#     # 3. Create a Dummy Pandas DataFrame (Simulating a file load)
#     data = {
#         'date_of_trans': ['2023-01-01', '2023-01-02'],
#         'inv_total': [500, 120],
#         'vendor_id': ['V1', 'V2'],
#         'random_col': ['A', 'B']
#     }
#     df_raw = pd.DataFrame(data)

#     # 4. Pass the WHOLE DataFrame to the mapper
#     # The class now handles extracting 'df_raw.columns' automatically
#     results, event_data = mapper.map_columns(df_raw)

#     # 5. Display Output
#     print("\n--- Mapping Results ---")
#     print(pd.DataFrame.from_dict(results, orient='index'))

#     assert True    


# def test_entity_resolver():
#     user_id = ""
#     # 1. Initialize Resolver with our "AI"
#     resolver = EntityResolver(user_id)

#     # 2. Create Messy Data (10 rows, but only 3 unique entities)
#     raw_data = pd.Series([
#         "ibm intl", "IBM", "amazon web svcs", "aws", 
#         "Uber Eats", "UBER", "ibm intl", "aws", "Unknown Vendor", None
#     ])

#     print("--- 1. Raw Data ---")
#     print(raw_data.values)

#     # 3. Resolve
#     clean_data = asyncio.run(resolver.resolve(raw_data))

#     print("\n--- 2. Resolved Data ---")
#     print(clean_data.values)
    
#     print("\n--- 3. Cache Stats ---")
#     # Shows we only paid for 6 resolutions, not 10
#     print(resolver.resolution_cache)

#     assert True