# import asyncio
# from pipeline import run_pipeline
# from .utils import build_test_payload

# # NOTE: We do NOT import 'app' from main here because we are hitting the network.


# def test_pipeline():
#     # Setup: Create a user ID/Session
#     payload = build_test_payload(type="csv", file_name="sample_data/normal_data/finance.csv", )
#     user_id = ""

#     print(payload)

#     asyncio.run(run_pipeline(payload=payload, user_id=user_id))

#     assert True