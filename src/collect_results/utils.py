from src.utils import unzip_file
import os
import json


def read_solvability_JSON(file_list):
    json_obj_list = []
    for file in file_list:
        file_name = file[:-len(".zip")]
        json_file = file_name + ".solvability.JSON"
        unzip_file(json_file+".zip")
        if os.path.exists(json_file):
            json_obj = {}
            json_obj["file_name"] = json_file
            with open(json_file) as f:
                loaded_graph = json.load(f)
                for field in loaded_graph:
                    # print(bcolors.GRENN + str(field) + str(loaded_graph[field]) + bcolors.RESET)
                    json_obj[str(field)] = loaded_graph[field]
            json_obj_list.append(json_obj)

        #delete unziped file
        if os.path.exists(json_file+".zip"):
            os.remove(json_file)
    return json_obj_list