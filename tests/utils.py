import csv

def build_test_payload(type, department="", user_input="", table_name="", connection_string="", file_name="", limit=0):

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
            payload["data_or_string"] = [file.read()]

    elif type == "json":
        pass
    elif type == "xlsx":
        pass
    else:
        payload["data_or_string"] = connection_string

    payload["credentials"] = 'testcredentials123',
    payload["limit"] = limit
    payload["table_name"] = table_name
    payload["department"] = department
    payload["user_input"] = user_input

    return payload
    