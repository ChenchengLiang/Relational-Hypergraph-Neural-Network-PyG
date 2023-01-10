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

    run_one_experiment(parameter_dict["model"], parameter_dict["task"], parameter_dict["num_gnn_layer"],
                       parameter_dict["benchmark"], parameter_dict["data_shuffle"], parameter_dict["gnn"],
                       parameter_dict["use_intermediate_gnn_results"],
                       parameter_dict["epochs"], parameter_dict["file_name"],
                       _reload_data=parameter_dict["reload_data"],
                       _self_loop=parameter_dict["self_loop"], _add_backward_edges=parameter_dict["add_backward_edges"],
                       _add_global_edges=parameter_dict["add_global_edges"],
                       _fix_random_seeds=parameter_dict["fix_random_seeds"],
                       _experiment_date=parameter_dict["experiment_date"], _dropout_rate=parameter_dict["dropout_rate"],
                       _num_linear_layer=parameter_dict["num_linear_layer"],
                       _use_class_weight=parameter_dict["use_class_weight"],
                       _experiment_name=experiment_name, _gradient_clip=parameter_dict["gradient_clip"],
                       _learning_rate=parameter_dict["learning_rate"], _activation=parameter_dict["activation"],
                       _cdhg_edge_types=parameter_dict["cdhg_edge_types"]
                       , _cg_edge_types=parameter_dict["cg_edge_types"],
                       _message_normalization=parameter_dict["message_normalization"],
                       _inter_layer_norm=parameter_dict["parameter_dict"])

    shutil.rmtree(temp_folder_path)


if __name__ == '__main__':
    main()
