import os
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
from src.utils import write_predicted_label_to_JSON_file, send_email
from torch_geometric.profile import get_model_size, count_parameters, get_data_size
from torch_geometric.profile.utils import byte_to_megabyte
#import wandb


def run_one_experiment(_model, _task, _num_gnn_layers, _benchmark, data_shuffle, _gnn, _use_intermediate_gnn_results,
                       _epochs, _file_name="", _reload_data=True,
                       _self_loop=False, _add_backward_edges=False, _add_global_edges=False, _fix_random_seeds=True,
                       _experiment_date=True,
                       _dropout_rate={"gnn_dropout_rate": 0, "mlp_dropout_rate": 0, "gnn_inner_layer_dropout_rate": 0},
                       _num_linear_layer=4, _use_class_weight=True, _experiment_name="",
                       _gradient_clip=False) -> object:
    if _fix_random_seeds == True:
        np.random.seed(42)
        torch.manual_seed(42)
        torch.cuda.manual_seed_all(42)



    # set experiment name
    today = datetime.today().strftime('%Y-%m-%d')
    experiment_name = _benchmark if _experiment_name == "" else _experiment_name
    mlflow_experiment_name = today + "-" + os.path.basename(
        experiment_name) if _experiment_date == True else os.path.basename(experiment_name)
    print("mlflow_experiment_name:", mlflow_experiment_name)

    #wandb_run = wandb.init(project=mlflow_experiment_name,reinit=True)

    mlflow.set_experiment(mlflow_experiment_name)
    mlflow.set_tracking_uri("http://localhost:5000")  # Specify tracking server
    task_num_class_dict = {"argument_binary_classification": 2, "template_binary_classification": 2,
                           "unsat_core_binary_classification": 2,
                           "template_multi_classification": 5}
    gnn_name_map = {"GCNConv": GCNConv, "SAGEConv": SAGEConv, "FiLMConv": FiLMConv, "HyperConv": HyperConv}

    params = {}
    params["benchmark"] = _benchmark
    params["learning_task"] = _task
    params["model"] = _model
    params["epochs"] = _epochs
    params["num_classes"] = task_num_class_dict[params["learning_task"]]
    params["task_type"] = "multi_classification" if params["num_classes"] > 2 else "binary_classification"
    params["embedding_size"] = 32
    params["num_gnn_layers"] = _num_gnn_layers
    params["num_linear_layer"] = _num_linear_layer
    params["graph_type"] = "hyperEdgeGraph" if "CDHG" in _benchmark else "monoDirectionLayerGraph"
    params["batch_size"] = 1
    params["add_self_loop_edges"] = _self_loop
    params["add_backward_edges"] = _add_backward_edges
    params["add_global_edges"] = _add_global_edges
    params["activation"] = "relu"  # leak_relu, tanh
    params["data_loader_shuffle"] = data_shuffle
    params["drop_out_rate"] = _dropout_rate
    params["learning_rate"] = 0.01
    params["gnn"] = gnn_name_map[_gnn]
    params["use_intermediate_gnn_results"] = _use_intermediate_gnn_results
    params["file_name"] = _file_name
    params["gradient_clip"] = _gradient_clip
    params["use_class_weight"] = _use_class_weight

    with mlflow.start_run(description=""):
        edge_arity_dict, train_loader, valid_loader, test_loader, vocabulary_size, params = get_data(params,
                                                                                                     reload_data=_reload_data)

        # todo: fix embedding layer outside of the training, otherwise random seed will affect them.

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # device = torch.device('cpu')

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
                                         edge_arity_dict=edge_arity_dict, embedding_size=params["embedding_size"],
                                         num_gnn_layers=params["num_gnn_layers"],
                                         num_linear_layer=params["num_linear_layer"],
                                         activation=params["activation"],
                                         dropout_probability=params["drop_out_rate"],
                                         use_intermediate_gnn_results=params["use_intermediate_gnn_results"]).to(device)
        else:
            model = Full_connected_model(params["num_classes"], vocabulary_size,
                                         embedding_size=params["embedding_size"]).to(device)
        # print("_benchmark",_benchmark)
        print("count_parameters", count_parameters(model))
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
