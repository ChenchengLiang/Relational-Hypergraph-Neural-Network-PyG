from torch_geometric.datasets import TUDataset,Planetoid,FakeDataset,PPI,MoleculeNet
from torch_geometric.loader import DataLoader
from torch_geometric.data import Dataset, Data
import torch
from models import GNN_classification,Hyper_classification
from train import train
import mlflow
from predict import predict
import numpy as np
def hyper_GNN_on_standard_dataset():
    np.random.seed(42)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    mlflow.set_experiment("2022-10-18-standard-dataset")
    params={}
    params["embedding_size"]=32
    params["num_gnn_layers"]=2
    params["num_linear_layer"]=4
    params["activation"]="leak_relu"
    params["epochs"]=1000
    params["drop_out_rate"]=0
    params["benchmark"]="Random"
    params["class_weight"]=[]
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if params["benchmark"]=="Cora":
        dataset = Planetoid(root='/tmp/'+params["benchmark"], name=params["benchmark"])
    elif params["benchmark"]=="Random":
        dataset = FakeDataset(num_graphs=10,avg_num_nodes=1000,avg_degree=5,num_channels=21,num_classes=7,task="node")
    elif params["benchmark"]=="MoleculeNet":
        dataset = MoleculeNet(root='/tmp/'+params["benchmark"],name="MUV")
    else:
        dataset = FakeDataset(num_graphs=10, avg_num_nodes=1000, avg_degree=10, num_channels=21, num_classes=7,
                              task="node")
    for data in dataset:
        data["target_indices"]=torch.tensor([i for i in range(len(data["x"]))])
        data["edge_list"]=[data["edge_index"]]
        #print(data)

    print("-"*20)
    params["feature_size"]=dataset.num_node_features
    params["num_classes"]=dataset.num_classes
    print("num_classes",params["num_classes"],"num_node_features",params["feature_size"])
    params["task_type"] = "multi_classification" if params["num_classes"] > 2 else "binary_classification"
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False,collate_fn=collate_fn)
    valid_loader=train_loader
    test_loader=train_loader

    with mlflow.start_run(description=""):
        model = GNN_classification(params["num_classes"], vocabulary_size=1, embedding_size=params["embedding_size"],
                                   num_gnn_layers=params["num_gnn_layers"], num_linear_layer=params["num_linear_layer"],
                                   activation=params["activation"],feature_size=params["feature_size"]).to(device)

        edge_arity_dict={"edge_type_0":2}
        # model = Hyper_classification(params["num_classes"], edge_arity_dict=edge_arity_dict,vocabulary_size=1, embedding_size=params["embedding_size"],
        #                            num_gnn_layers=params["num_gnn_layers"], num_linear_layer=params["num_linear_layer"],
        #                            activation=params["activation"], feature_size=params["feature_size"],drop_out_probability=params["drop_out_rate"]).to(device)


        trained_model, optimizer = train(train_loader, valid_loader, model, params)

        print("-" * 10 + "best_model" + "-" * 10)
        model_path = "../models/best_model.pth"
        best_model = torch.load(model_path)
        mlflow.pytorch.log_model(best_model, "model")
        predicted_list, raw_predicted_list, file_name_list = predict(best_model, test_loader, optimizer, params)

def collate_fn(data):
    for d in data:
        d["target_indices"] = torch.tensor([i for i in range(len(d["x"]))])
        d["edge_list"] = [d["edge_index"]]
        d["file_name"]="file_name"
    return data

if __name__ == '__main__':
    hyper_GNN_on_standard_dataset()