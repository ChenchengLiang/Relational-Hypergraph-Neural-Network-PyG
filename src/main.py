import os
from os.path import join as opj
from dataset import HornGraphDataset
from torch_geometric.loader import DataLoader
from models import Hyper_classification, Full_connected_model, GNN_classification
from train import train
import numpy as np
import torch
from utils import remove_processed_file, write_predicted_label_to_JSON_file
from train_utils import get_loss_function
from predict import predict
import mlflow
from plots import draw_label_pie_chart


def main():
    np.random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    #benchmarks = ["../data/experiment-"+str(i) for i in range(13)]
    benchmarks = ["../data/experiment-template-binary-classification"]
    #models=["GCN","hyper_GCN","full_connected"]
    models = ["hyper_GCN","GCN"]
    #tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification"]
    tasks = ["argument_binary_classification"]
    graph_types=["hyperEdgeGraph","monoDirectionLayerGraph"]
    #graph_types = ["monoDirectionLayerGraph"]
    #graph_types = ["hyperEdgeGraph"]
    num_gnn_layers=[1,2,4,8]
    #num_gnn_layers = [2]

    for graph_type in graph_types:
        for bench in benchmarks:
            for model in models:
                for task in tasks:
                    for num_gnn_layer in num_gnn_layers:
                        run_one_experiment(model,task,graph_type,num_gnn_layer,bench)

def run_one_experiment(_model,_task,_graph_type,_num_gnn_layers,_benchmark):
    mlflow.set_experiment("2022-10-17-argument-classification")
    task_num_class_dict={"argument_binary_classification":2,"template_binary_classification":2,"template_multi_classification":5}

    params = {}
    params["benchmark"] = _benchmark
    params["learning_task"] = _task
    params["model"] = _model
    params["epochs"] = 100
    params["num_classes"] = task_num_class_dict[params["learning_task"]]
    params["task_type"] = "multi_classification" if params["num_classes"] > 2 else "binary_classification"
    params["embedding_size"] = 32
    params["num_gnn_layers"] = _num_gnn_layers
    params["num_linear_layer"] = 2
    params["graph_type"] = _graph_type
    params["batch_size"] = 1
    params["self_loop"] = True
    params["activation"]="leak_relu" #leak_relu, tanh



    with mlflow.start_run(description=""):
        edge_arity_dict,train_loader,valid_loader,test_loader,vocabulary_size,class_weight,params=get_data(params, params["benchmark"])

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        if params["model"] == "GCN":
            model = GNN_classification(params["num_classes"], vocabulary_size, embedding_size=params["embedding_size"],
                                       num_gnn_layers=params["num_gnn_layers"],num_linear_layer=params["num_linear_layer"],
                                       activation=params["activation"]).to(
                device)
        elif params["model"]=="hyper_GCN":
            model = Hyper_classification(params["num_classes"],
                                         vocabulary_size=vocabulary_size,
                                         edge_arity_dict=edge_arity_dict, embedding_size=params["embedding_size"],
                                         num_gnn_layers=params["num_gnn_layers"], num_linear_layer=params["num_linear_layer"],
                                         activation=params["activation"]).to(device)
        else:
            model = Full_connected_model(params["num_classes"],vocabulary_size,embedding_size=params["embedding_size"]).to(device)



        ls_func = get_loss_function(params["task_type"],class_weight).to(device)
        trained_model, optimizer = train(train_loader, valid_loader, model, ls_func, epochs=params["epochs"],
                                         task_type=params["task_type"])

        # print("-" * 10 + "trained_model" + "-" * 10)
        # predict(trained_model, test_loader, optimizer, ls_func,params["num_classes"], task_type=params["task_type"])

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = "../models/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list = predict(best_model, test_loader, optimizer, ls_func,
                                                                     params["num_classes"],
                                                                     task_type=params["task_type"])

    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list,params["task_type"], root=opj(params["benchmark"],"test_data"))




def get_data(params,benchmark):
    root = opj(benchmark, "train_data")
    remove_processed_file(root=root)
    train_data = HornGraphDataset(root=root, learning_task=params["learning_task"], num_classes=params["num_classes"],
                                  graph_type=params["graph_type"],self_loop=params["self_loop"])

    root = opj(benchmark, "valid_data")
    remove_processed_file(root=root)
    valid_data = HornGraphDataset(root=root, learning_task=params["learning_task"], num_classes=params["num_classes"],
                                  graph_type=params["graph_type"],self_loop=params["self_loop"])

    root = opj(benchmark, "test_data")
    remove_processed_file(root=root)
    test_data = HornGraphDataset(root=root, learning_task=params["learning_task"], num_classes=params["num_classes"],
                                 graph_type=params["graph_type"],self_loop=params["self_loop"])

    dataset = train_data + valid_data + test_data
    vocabulary_size = len(train_data.vocabulary) + len(valid_data.vocabulary) + len(test_data.vocabulary)

    # train_data = dataset
    # valid_data = train_data
    # test_data = train_data
    print("train-valid-test:", len(train_data), len(valid_data), len(test_data))
    print("train_data[0]", train_data[0])
    # print("train_data[0].y", train_data[0].y)

    train_loader = DataLoader(train_data, batch_size=params["batch_size"], shuffle=True)
    valid_loader = DataLoader(valid_data, batch_size=params["batch_size"], shuffle=True)
    test_loader = DataLoader(test_data, batch_size=params["batch_size"], shuffle=True)

    edge_arity_dict = train_data[0].edge_arity_dict

    dataset_distribution_values = draw_label_pie_chart(params["num_classes"], [t.y for t in dataset], "all-data")
    draw_label_pie_chart(params["num_classes"], [t.y for t in train_data], "train-data")
    draw_label_pie_chart(params["num_classes"], [t.y for t in valid_data], "valid-data")
    draw_label_pie_chart(params["num_classes"], [t.y for t in test_data], "test-data")
    class_weight = [1 - (v / sum(dataset_distribution_values)) for v in dataset_distribution_values]
    params["class_weight"] = class_weight
    params["edge_arity_dict"]=edge_arity_dict
    mlflow.log_params(params)
    mlflow.log_dict(params, "params.json")

    return edge_arity_dict,train_loader,valid_loader,test_loader,vocabulary_size,class_weight,params


if __name__ == '__main__':
    main()

