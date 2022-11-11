import os
from datetime import datetime
from os.path import join as opj

import mlflow
import numpy as np
import torch
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv

from models import Hyper_classification, Full_connected_model, GNN_classification
from predict import predict
from src.data_utils.read_data import get_data
from train import train
from utils import write_predicted_label_to_JSON_file


def main():
    np.random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    # benchmarks = ["../data/experiment-"+str(i) for i in range(13)]
    #benchmarks = ["../data/experiment-template-binary-classification"]
    benchmarks = ["../data/linear_dataset_shuffled"]
    #models = [ "hyper_GCN","GNN"]
    models = [ "hyper_GCN"]
    gnns=[SAGEConv,FiLMConv,GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification"]
    tasks = ["template_binary_classification"]
    graph_types = ["hyperEdgeGraph", "monoDirectionLayerGraph"]
    #graph_types = ["monoDirectionLayerGraph"]
    #graph_types = ["hyperEdgeGraph"]
    num_gnn_layers = [2]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results=[True,False]

    for graph_type in graph_types:
        for bench in benchmarks:
            for model in models:
                for task in tasks:
                    for num_gnn_layer in num_gnn_layers:
                        for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                            for data_shuffle in data_loader_shuffle:
                                if model == "GNN":
                                    for _gnn in gnns:
                                        run_one_experiment(model, task, graph_type, num_gnn_layer, bench, data_shuffle,_gnn,_use_intermediate_gnn_results)
                                else:
                                    run_one_experiment(model, task, graph_type, num_gnn_layer, bench, data_shuffle, SAGEConv,_use_intermediate_gnn_results)


def run_one_experiment(_model, _task, _graph_type, _num_gnn_layers, _benchmark, data_shuffle,_gnn,_use_intermediate_gnn_results):
    today=datetime.today().strftime('%Y-%m-%d')
    mlflow.set_experiment(today+"-"+os.path.basename(_benchmark))
    task_num_class_dict = {"argument_binary_classification": 2, "template_binary_classification": 2,
                           "template_multi_classification": 5}

    params = {}
    params["benchmark"] = _benchmark
    params["learning_task"] = _task
    params["model"] = _model
    params["epochs"] = 200
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

        trained_model, optimizer = train(train_loader, valid_loader, model, params)

        # print("-" * 10 + "trained_model" + "-" * 10)
        # predict(trained_model, test_loader, optimizer, ls_func,params["num_classes"], task_type=params["task_type"])

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = "../models/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list = predict(best_model, test_loader, optimizer, params)

        params["gnn"] = str(params["gnn"])[str(params["gnn"]).rfind(".") + 1:-2]
        mlflow.log_params(params)
        mlflow.log_dict(params, "params.json")

    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list, params["task_type"],
                                       root=opj(params["benchmark"], "test_data"))



if __name__ == '__main__':
    main()
