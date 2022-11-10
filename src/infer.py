import mlflow
import torch
from predict import predict
from os.path import join as opj
from train_utils import get_loss_function
from utils import remove_processed_file,write_predicted_label_to_JSON_file
from src.data_utils.dataset import HornGraphDataset
from torch_geometric.loader import DataLoader
def infer():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    artifact_uri = "./mlruns/4/d4114f79216542c9a1e3f166044c1023/artifacts"
    model_path = opj(artifact_uri,"model/data/model.pth")
    best_model = torch.load(model_path)
    #mlflow.pytorch.load_model()
    params=mlflow.artifacts.load_dict(opj(artifact_uri,"params.json"))
    ls_func = get_loss_function(params).to(device)
    optimizer = torch.optim.Adam(best_model.parameters(), lr=0.01, weight_decay=5e-4)

    #Load test data
    benchmark="../data/infer"
    root = opj(benchmark, "test_data")
    remove_processed_file(root=root)
    test_data = HornGraphDataset(root=root, learning_task=params["learning_task"], num_classes=params["num_classes"],
                                 graph_type=params["graph_type"],self_loop=params["self_loop"])
    test_loader = DataLoader(test_data, batch_size=params["batch_size"], shuffle=True)

    #predict
    mlflow.set_experiment("infer")
    with mlflow.start_run(description=""):
        predicted_list, raw_predicted_list, file_name_list = predict(best_model, test_loader, optimizer, params)
    #write back to graph
    write_predicted_label_to_JSON_file(predicted_list, raw_predicted_list, file_name_list,params["task_type"], root=root)

if __name__ == '__main__':
    infer()