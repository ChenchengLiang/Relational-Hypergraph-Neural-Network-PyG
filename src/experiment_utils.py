import os
import random
from datetime import datetime
from os.path import join as opj
import mlflow
import numpy as np
import torch
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from src.models import Hyper_classification, Full_connected_model, GNN_classification
from src.predict import predict
from src.data_utils.read_data import get_data
from src.train import train
from src.utils import write_predicted_label_to_JSON_file, send_email,compress_data
from src.cluster_utils.utils import get_task_by_folder_name
from src.train_utils import get_parameter_summary
from torch_geometric.profile import get_model_size, count_parameters, get_data_size
from torch_geometric.profile.utils import byte_to_megabyte
import glob
import sys
sys.path.append("../")


# import wandb

def get_default_parameters():
    return {
        "model":"hyper_GCN",
        "learning_task":"unsatcore_binary_classification",
        "num_gnn_layers":2,
        "benchmark":"",
        "data_loader_shuffle": False,
        "gnn":HyperConv.__name__,
        "use_intermediate_gnn_results":False,
        "epochs":2,
        "file_name":"",
        "reload_data":False,
        "add_self_loop_edges":False,
        "add_backward_edges":False,
        "add_global_edges":False,
        "fix_random_seeds":True,
        "experiment_date":True,
        "drop_out_rate":{"gnn_dropout_rate": 0, "mlp_dropout_rate": 0, "gnn_inner_layer_dropout_rate": 0},
        "num_linear_layer":2,
        "use_class_weight":True,
        "experiment_name":"",
        "gradient_clip":True,
        "learning_rate":0.001,
        "activation":"relu",# relu,leak_relu, tanh
        "cdhg_edge_types":["relationSymbolArgumentEdge", "guardEdge",
                       "ASTLeftEdge", "ASTRightEdge",
                       # "ASTEdge",
                       # "quantifierEdge",
                       "controlFlowHyperEdge", "dataFlowHyperEdge"],
        "cg_edge_types":["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
                     "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge",
                     # "ASTLeftEdge", "ASTRightEdge",
                     "ASTEdge",
                     # "quantifierEdge",
                     "guardEdge", "dataEdge",
                     ],
        "edge_types":[],
        "embedding_size":64,
        "message_normalization":False,
        "inter_layer_norm":True,
        "GPU":True,
        "regression_layer_norm":False,
        "patient":2,
        "batch_size":1,
    }

def run_one_experiment(input_params
                       # ,_model, _task, _num_gnn_layers, _benchmark, data_shuffle, _gnn, _use_intermediate_gnn_results,
                       # _epochs, _file_name="", _reload_data=True,
                       # _self_loop=False, _add_backward_edges=False, _add_global_edges=False, _fix_random_seeds=True,
                       # _experiment_date=True,
                       # _dropout_rate={"gnn_dropout_rate": 0, "mlp_dropout_rate": 0, "gnn_inner_layer_dropout_rate": 0},
                       # _num_linear_layer=4, _use_class_weight=True, _experiment_name="",
                       # _gradient_clip=False, _learning_rate=0.001, _activation="relu", _cdhg_edge_types=[],
                       # _cg_edge_types=[], _embedding_size=64, _message_normalization=False,_inter_layer_norm=True,
                       # _GPU=True,_regression_layer_norm=True,_patient=20
                       ) -> object:
    compress_files(input_params["benchmark"])

    gnn_name_map = {"GCNConv": GCNConv, "SAGEConv": SAGEConv, "FiLMConv": FiLMConv, "HyperConv": HyperConv}
    task_num_class_dict = {"argument_binary_classification": 2, "template_binary_classification": 2,
                           "unsatcore_binary_classification": 2,
                           "template_multi_classification": 5}

    params=get_default_parameters()
    input_params["gnn"]=gnn_name_map[input_params["gnn"]]
    input_params["edge_types"]=input_params["cdhg_edge_types"] if "CDHG" in input_params["benchmark"] else input_params["cg_edge_types"]
    input_params["learning_task"]=get_task_by_folder_name(input_params["benchmark"])
    input_params["num_classes"]=task_num_class_dict[input_params["learning_task"]]
    input_params["task_type"] = "multi_classification" if input_params["num_classes"] > 2 else "binary_classification"
    input_params["graph_type"] = "hyperEdgeGraph" if "CDHG" in input_params["benchmark"] else "monoDirectionLayerGraph"
    params.update(input_params)

    if params["fix_random_seeds"] == True:
        np.random.seed(42)
        random.seed(42)
        torch.manual_seed(42)
        torch.cuda.manual_seed_all(42)

    # set experiment name
    today = datetime.today().strftime('%Y-%m-%d')
    experiment_name = params["benchmark"] if params["experiment_name"] == "" else params["experiment_name"]
    mlflow_experiment_name = today + "-" + os.path.basename(
        experiment_name) if params["experiment_date"] == True else os.path.basename(experiment_name)
    print("mlflow_experiment_name:", mlflow_experiment_name)

    # wandb_run = wandb.init(project=mlflow_experiment_name,reinit=True)

    mlflow.set_experiment(mlflow_experiment_name)
    mlflow.set_tracking_uri("http://localhost:5000")  # Specify tracking server



    # params = {}
    # params["model"] = _model
    # params["learning_task"] = _task
    # params["num_gnn_layers"] = _num_gnn_layers
    # params["benchmark"] = _benchmark
    # params["data_loader_shuffle"] = data_shuffle
    # params["gnn"] = gnn_name_map[_gnn]
    # params["epochs"] = _epochs
    # params["file_name"] = _file_name
    # params["use_intermediate_gnn_results"] = _use_intermediate_gnn_results
    # params["add_self_loop_edges"] = _self_loop
    # params["add_backward_edges"] = _add_backward_edges
    # params["add_global_edges"] = _add_global_edges
    # params["drop_out_rate"] = _dropout_rate
    # params["num_linear_layer"] = _num_linear_layer
    # params["use_class_weight"] = _use_class_weight
    # params["gradient_clip"] = _gradient_clip
    # params["learning_rate"] = _learning_rate
    # params["activation"] = _activation  # relu,leak_relu, tanh
    # params["edge_types"] = _cdhg_edge_types if "CDHG" in _benchmark else _cg_edge_types
    # params["embedding_size"] = _embedding_size
    # params["message_normalization"] = _message_normalization
    # params["inter_layer_norm"] = _inter_layer_norm
    # params["GPU"] = _GPU
    # params["regression_layer_norm"] = _regression_layer_norm
    # params["fix_random_seeds"] = _fix_random_seeds
    # params["patient"] = _patient
    # params["batch_size"] = 1
    # params["num_classes"] = task_num_class_dict[params["learning_task"]]
    # params["task_type"] = "multi_classification" if params["num_classes"] > 2 else "binary_classification"
    # params["graph_type"] = "hyperEdgeGraph" if "CDHG" in _benchmark else "monoDirectionLayerGraph"
    #



    with mlflow.start_run(description=""):
        edge_arity_dict, train_loader, valid_loader, test_loader, vocabulary_size, params = get_data(params)
        # todo: fix embedding layer outside of the training, otherwise random seed will affect them.

        if params["GPU"]==True:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            device = torch.device('cpu')

        if params["model"] == "GNN":
            model = GNN_classification(params["num_classes"], vocabulary_size=vocabulary_size,
                                       edge_arity_dict=edge_arity_dict, embedding_size=params["embedding_size"],
                                       gnn=params["gnn"],
                                       num_gnn_layers=params["num_gnn_layers"],
                                       num_linear_layer=params["num_linear_layer"],
                                       activation=params["activation"]).to(device)
        elif params["model"] == "hyper_GCN":
            model = Hyper_classification(params["num_classes"],
                                         vocabulary_size=vocabulary_size,
                                         edge_arity_dict=edge_arity_dict, input_params=params).to(device)
        else:
            model = Full_connected_model(params["num_classes"], vocabulary_size,
                                         embedding_size=params["embedding_size"]).to(device)
        # print("_benchmark",_benchmark)

        get_parameter_summary(model)
        print("get_model_size", byte_to_megabyte(get_model_size(model)), "MB\n")

        params["gnn"] = str(params["gnn"])[str(params["gnn"]).rfind(".") + 1:-2]
        mlflow.log_params(params)
        mlflow.log_dict(params, "params.json")

        # wandb.config=params
        # wandb.log(params)
        # wandb.watch(model)

        trained_model = train(train_loader, valid_loader, model, device, params)

        # print("-" * 10 + "trained_model" + "-" * 10)
        # predict(trained_model, test_loader, optimizer, ls_func,params["num_classes"], task_type=params["task_type"])

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = params["benchmark"] + "/model/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list, predicted_accuracy = predict(trained_model=best_model,
                                                                                         test_loader=test_loader,
                                                                                         device=device, params=params)

    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list, params["task_type"],
                                       root=opj(params["benchmark"], "test_data"))
    return predicted_accuracy


def compress_files(benchmark):
    for fold in ["train_data","valid_data","test_data"]:
        folder=benchmark+"/"+fold+"/raw"
        if len(glob.glob(folder+"/*.zip"))==0 and len(glob.glob(folder+"/*"))!=0:
            compress_data(folder)

