import sys

# sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.experiment_utils import run_one_experiment
from src.utils import make_dirct
import shutil
import json
import os


def main():
    parameter_index = sys.argv[1]
    hyper_parameter_folder = "/cephyr/users/liangch/Alvis/training_code/hyper-parameters"
    # hyper_parameter_folder="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/hyper-parameters"
    json_file_name = hyper_parameter_folder + "/hyper-paprameter_" + str(parameter_index) + ".JSON"
    if os.path.exists(json_file_name):
        with open(json_file_name) as f:
            parameter_dict = json.load(f)
    else:
        print("file", json_file_name, "not existed")

    print("parameter_dict", parameter_dict)

    # create temp folder and set experiment name for each run
    experiment_name = os.path.basename(parameter_dict["benchmark"])
    temp_folder_path = parameter_dict["benchmark"] + "_" + str(parameter_index)
    shutil.copytree(parameter_dict["benchmark"], temp_folder_path)
    parameter_dict["benchmark"] = temp_folder_path
    parameter_dict["experiment_name"]=experiment_name

    run_one_experiment(parameter_dict)

    shutil.rmtree(temp_folder_path)


if __name__ == '__main__':
    main()
