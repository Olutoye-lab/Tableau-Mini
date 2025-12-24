
def build_test_payload(type, credentials={}, user_input="", file_name="", connection_string="", table_name="", limit=0):

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
            payload["data"] = [file.read()]

    elif type == "json":
        pass
    elif type == "xlsx":
        pass
    else:
        payload["data"] = connection_string

    payload["credentials"] = credentials,
    payload["limit"] = limit
    payload["table_name"] = table_name
    payload["user_input"] = user_input

    return payload
    