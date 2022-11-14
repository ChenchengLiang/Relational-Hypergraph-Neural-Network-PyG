from src.utils import unzip_file,make_dirct,convert_bytes
import os
import json
import glob
from shutil import copy
from tqdm import tqdm
def read_json_file(f,json_obj):
    loaded_graph = json.load(f)
    for field in loaded_graph:
        # print(bcolors.GRENN + str(field) + str(loaded_graph[field]) + bcolors.RESET)
        json_obj[str(field)] = loaded_graph[field]
    return json_obj

def read_files(file_list,file_type="solvability.JSON",read_function=read_json_file):
    for file in tqdm(file_list,desc="read " + file_type):
        file_name = file[:-len(".zip")]
        json_file = file_name + "."+file_type
        unzip_file(json_file+".zip")
        if os.path.exists(json_file):
            json_obj = {}
            json_obj["file_name"] = json_file
            json_obj["file_size"] = convert_bytes(os.path.getsize(json_file))
            with open(json_file) as f:
                read_function(f,json_obj)
                # delete unziped file
            if os.path.exists(json_file + ".zip"):
                os.remove(json_file)
            yield json_obj


def read_graph_generation_log(f,json_obj):
    for l in f.readlines():
        for g in ["CDHG","CG"]:
            if g in l:
                json_obj.update({g+"_time_consumption": int(l[l.find(":")+1:l.find("milliseconds")])})
    return json_obj

def get_sumary_folder(folder):
    summary_folder = os.path.dirname(folder) + "/" + os.path.basename(folder) + "_summary"
    make_dirct(summary_folder)
    return summary_folder

def copy_relative_files(file_name, folder):
    for f in glob.glob(file_name + "*"):
        copy(f, folder)