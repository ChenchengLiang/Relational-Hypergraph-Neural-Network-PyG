from src.utils import unzip_file
import os
import json

def main():
    print_filled_fields("solvingTime","random")


def print_filled_fields(key_word_1="",key_word_2=""):
    file_list = ["/home/cheli243/Desktop/eldarica/test/predicted/chc-LIA-non-lin_005.smt2.zip"]
    json_obj_list = read_solvability_JSON(file_list)
    collected_fields=[]
    for j in json_obj_list:
        for field in j:
            if j[field][0]!="10800000" and key_word_1 in field and key_word_2 in field:
                collected_fields.append([field,j[field]])
                #print(field,j[field])
    for f in sorted(collected_fields):
        print(f[0],f[1])

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

if __name__ == '__main__':
    main()