from train import run_one_epoch
import numpy as np
from utils import manual_flatten
import mlflow
from plots import draw_label_pie_chart, draw_confusion_matrix
from torch_utils import get_accuracy
from train_utils import get_loss_function
import torch

def predict(trained_model, test_loader, params):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    optimizer = torch.optim.Adam(trained_model.parameters(), lr=params["learning_rate"], weight_decay=5e-4)
    ls_func = get_loss_function(params).to(device)
    trained_model.eval()
    test_loss, predicted_list, raw_predicted_list, label_list, file_name_list = run_one_epoch(trained_model,
                                                                                              test_loader, optimizer,
                                                                                              ls_func,
                                                                                              train=False,
                                                                                              task_type=params["task_type"])

    print("test_loss:", test_loss)
    # print("raw_predicted_list", raw_predicted_list)
    # print("predicted_list[0]:", predicted_list[0])
    # print("label_list[0]:", label_list[0])
    mlflow.log_metric("test_loss", test_loss)
    draw_label_pie_chart(params["num_classes"], predicted_list, "predicted-data")

    print("-" * 10)
    acc, flatten_predicted_list, flatten_label_list = get_accuracy(predicted_list, label_list)
    # flatten_predicted_list = np.array(manual_flatten(predicted_list)).ravel()
    # flatten_label_list = np.array(manual_flatten(label_list)).ravel()
    draw_confusion_matrix(flatten_predicted_list, flatten_label_list, params["num_classes"])

    # correct = (flatten_predicted_list == flatten_label_list).sum()
    # acc = int(correct) / len(flatten_label_list)
    mlflow.log_metric("Predicted Accuracy", acc)
    print(f'Predicted Accuracy: {acc:.4f}')

    return predicted_list, raw_predicted_list, file_name_list
