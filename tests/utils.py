
import os
from dotenv import load_dotenv

load_dotenv()

def build_test_payload(type, file_name="", connection_string="", table_name="", limit=0):
    # --- types --- 
    # csv
    # json
    # xmls
    # string

    payload = {}
    payload["dataType"] = type

    if type == "csv":
        with open(file_name, mode='r') as file:
            # All files will be processed in pandas as strings
            payload["data"] = file.read()

    elif type == "json":
        pass
    elif type == "xlsx":
        pass
    else:
        payload["data"] = connection_string

    payload["limit"] = limit
    payload["table_name"] = table_name

    payload["token"] = os.getenv("TB_TOKEN") or ""
    payload["token_name"] = os.getenv("TB_TOKEN_NAME") or ""
    payload["server_url"] = os.getenv("TB_SERVER_URL") or ""
    payload["site_name"] = os.getenv("TB_SITE_NAME") or ""

    return payload
    