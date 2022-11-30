import os
from datetime import datetime
from os.path import join as opj
import mlflow
import numpy as np
import torch
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.models import Hyper_classification, Full_connected_model, GNN_classification
from src.predict import predict
from src.data_utils.read_data import get_data
from src.train import train
from src.utils import write_predicted_label_to_JSON_file, send_email
from torch_geometric.profile import get_model_size, count_parameters, get_data_size
from torch_geometric.profile.utils import byte_to_megabyte


def run_one_experiment(_model, _task, _num_gnn_layers, _benchmark, data_shuffle, _gnn, _use_intermediate_gnn_results,
                       _epochs, _file_name="", _reload_data=True,
                       _self_loop=False,_add_backward_edge=False, _fix_random_seeds=True, _experiment_date=True) -> object:
    if _fix_random_seeds == True:
        np.random.seed(42)
        torch.manual_seed(42)
        torch.cuda.manual_seed_all(42)

    today = datetime.today().strftime('%Y-%m-%d')
    mlflow_experiment_name = today + "-" + os.path.basename(_benchmark) if _experiment_date==True else os.path.basename(_benchmark)
    print("mlflow_experiment_name:", mlflow_experiment_name)
    mlflow.set_experiment(mlflow_experiment_name)
    mlflow.set_tracking_uri("http://localhost:5000")  # Specify tracking server
    task_num_class_dict = {"argument_binary_classification": 2, "template_binary_classification": 2,"unsat_core_binary_classification":2,
                           "template_multi_classification": 5}

    params = {}
    params["benchmark"] = _benchmark
    params["learning_task"] = _task
    params["model"] = _model
    params["epochs"] = _epochs
    params["num_classes"] = task_num_class_dict[params["learning_task"]]
    params["task_type"] = "multi_classification" if params["num_classes"] > 2 else "binary_classification"
    params["embedding_size"] = 32
    params["num_gnn_layers"] = _num_gnn_layers
    params["num_linear_layer"] = 2
    params["graph_type"] = "hyperEdgeGraph" if "CDHG" in _benchmark else "monoDirectionLayerGraph"
    params["batch_size"] = 1
    params["add_self_loop_edges"] = _self_loop
    params["add_backward_edges"] = _add_backward_edge
    params["activation"] = "relu"  # leak_relu, tanh
    params["data_loader_shuffle"] = data_shuffle
    params["drop_out_rate"] = 0.1
    params["learning_rate"] = 0.001
    params["gnn"] = _gnn
    params["use_intermediate_gnn_results"] = _use_intermediate_gnn_results
    params["file_name"] = _file_name
    params["gradient_clip"] = True

    with mlflow.start_run(description=""):
        edge_arity_dict, train_loader, valid_loader, test_loader, vocabulary_size, params = get_data(params,
                                                                                                     reload_data=_reload_data)

        #todo: fix embedding layer outside of the training, otherwise random seed will affect them.

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # device = torch.device('cpu')

        if params["model"] == "GNN":
            model = GNN_classification(params["num_classes"], vocabulary_size, embedding_size=params["embedding_size"],
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
                                         drop_out_probability=params["drop_out_rate"],
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

        trained_model = train(train_loader, valid_loader, model, device, params)

        # print("-" * 10 + "trained_model" + "-" * 10)
        # predict(trained_model, test_loader, optimizer, ls_func,params["num_classes"], task_type=params["task_type"])

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = "../models/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list, predicted_accuracy = predict(trained_model=best_model,
                                                                                         test_loader=test_loader,
                                                                                         device=device, params=params)

    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list, params["task_type"],
                                       root=opj(params["benchmark"], "test_data"))
    return predicted_accuracy
