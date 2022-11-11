import mlflow
import torch
from predict import predict
from utils import remove_processed_file,write_predicted_label_to_JSON_file
from src.data_utils.dataset import HornGraphDataset
from torch_geometric.loader import DataLoader
from data_utils.read_data import build_vocabulary
from os.path import join as opj
def main():
    data_path="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/data"
    benchmark_dict={opj(data_path,"linear-unsolvable-predict-CDHG"):
                        "./mlruns/1/764e9c18cfdd4700b7a573cd3bbe54f4/artifacts",
                    opj(data_path,"linear-unsolvable-predict-CG"):
                    "./mlruns/1/528002b450324df6b16e61909c09f4ed/artifacts"}
    for k in benchmark_dict:
        infer(k,benchmark_dict[k])

def infer(benchmark,artifact_uri):

    model_path = opj(artifact_uri,"model/data/model.pth")
    best_model = torch.load(model_path)
    #mlflow.pytorch.load_model()
    params=mlflow.artifacts.load_dict(opj(artifact_uri,"params.json"))
    #optimizer = torch.optim.Adam(best_model.parameters(), lr=params["learning_rate"], weight_decay=5e-4)

    #Load test data
    vocabulary, token_map = build_vocabulary(params)
    root = opj(benchmark, "test_data")
    remove_processed_file(root=root)
    test_data = HornGraphDataset(params=params, root=root, token_map=token_map)
    test_loader = DataLoader(test_data, batch_size=params["batch_size"], shuffle=True)

    #predict
    mlflow.set_experiment("infer")
    with mlflow.start_run(description=""):
        predicted_list, raw_predicted_list, file_name_list = predict(best_model, test_loader, params)
    #write back to graph
    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list,params["task_type"], root=root)

if __name__ == '__main__':
    main()