import os

import mlflow
import torch
from src.predict import predict
from src.utils import remove_processed_file, write_predicted_label_to_JSON_file
from src.data_utils.dataset import HornGraphDataset
from torch_geometric.loader import DataLoader
from os.path import join as opj
from datetime import datetime


def infer(benchmark, artifact_uri):
    device = torch.device("cpu")  # torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = opj(artifact_uri, "model/data/model.pth")
    best_model = torch.load(model_path).to(device)
    # mlflow.pytorch.load_model()
    params = mlflow.artifacts.load_dict(opj(artifact_uri, "params.json"))
    params["benchmark"] = benchmark


    # Load test data
    token_map = mlflow.artifacts.load_dict(opj(artifact_uri, "token_map.json"))
    print("token_map", len(token_map))
    root = opj(benchmark, "test_data")

    if os.path.exists(params["benchmark"] + "/test/processed/data_0.pt"):
        params["reload_data"] = False
    else:
        params["reload_data"] = True
        remove_processed_file(root=root)

    test_data = HornGraphDataset(params=params, root=root, token_map=token_map)
    test_loader = DataLoader(test_data, batch_size=params["batch_size"], shuffle=False)

    # predict
    today = datetime.today().strftime('%Y-%m-%d')
    mlflow_experiment_name = today + "-infer"
    print("mlflow_experiment_name", mlflow_experiment_name)
    mlflow.set_experiment(mlflow_experiment_name)

    with mlflow.start_run(description=""):
        predicted_list, raw_predicted_list, file_name_list, predicted_accuracy = predict(best_model, test_loader,
                                                                                         device,
                                                                                         params)
        mlflow.log_params(params)
    # write back to graph
    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list, params["task_type"],
                                       root=root)
