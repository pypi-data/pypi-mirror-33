import json

from properly_util_python.clean_data import clean_data_very_clean, clean_data_general
from properly_util_python.helper_utils import download_files
from properly_util_python.dynamo_utils import save_to_dynamo
s3_file_keys = []


def json_to_dynamo(table_name):
    local_files = download_files(s3_file_keys)

    for file in local_files:
        data = json.load(open(file))

        clean_data = data[:]
        for i in range(len(data)):
            clean_data[i] = clean_data_general(data[i])
            # todo check if exists in dynamo
            save_to_dynamo(table_name, clean_data[i])

        # for i in range(len(data)):
        #     clean_data[i] = clean_data_very_clean(data[i])
        #     save_to_dynamo('dev-property-historical-clean', clean_data[i])
