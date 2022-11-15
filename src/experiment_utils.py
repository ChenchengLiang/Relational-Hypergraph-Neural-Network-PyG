
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
from src.utils import write_predicted_label_to_JSON_file,send_email
from torch_geometric.profile import get_model_size,count_parameters,get_data_size
from torch_geometric.profile.utils import byte_to_megabyte

def run_one_experiment(_model, _task, _graph_type, _num_gnn_layers, _benchmark, data_shuffle,_gnn,_use_intermediate_gnn_results,_epochs):
    today=datetime.today().strftime('%Y-%m-%d')
    mlflow.set_experiment(today+"-"+os.path.basename(_benchmark))
    task_num_class_dict = {"argument_binary_classification": 2, "template_binary_classification": 2,
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
    params["graph_type"] = _graph_type
    params["batch_size"] = 1
    params["self_loop"] = False
    params["activation"] = "leak_relu"  # leak_relu, tanh
    params["data_loader_shuffle"] = data_shuffle
    params["drop_out_rate"] = 0
    params["learning_rate"] = 0.001
    params["gnn"] = _gnn
    params["use_intermediate_gnn_results"]=_use_intermediate_gnn_results

    with mlflow.start_run(description=""):
        edge_arity_dict, train_loader, valid_loader, test_loader, vocabulary_size, params = get_data(params,reload_data=True)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        #device = torch.device('cpu')

        if params["model"] == "GNN":
            model = GNN_classification(params["num_classes"], vocabulary_size, embedding_size=params["embedding_size"],gnn=params["gnn"],
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
        print("count_parameters",count_parameters(model))
        print("get_model_size",byte_to_megabyte(get_model_size(model)),"MB\n")
        trained_model = train(train_loader, valid_loader, model, params)

        # print("-" * 10 + "trained_model" + "-" * 10)
        # predict(trained_model, test_loader, optimizer, ls_func,params["num_classes"], task_type=params["task_type"])

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/models/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list, predicted_sccuracy = predict(best_model, test_loader, params)

        params["gnn"] = str(params["gnn"])[str(params["gnn"]).rfind(".") + 1:-2]
        mlflow.log_params(params)
        mlflow.log_dict(params, "params.json")

    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list, params["task_type"],
                                       root=opj(params["benchmark"], "test_data"))
    return predicted_sccuracy