from src.train import run_one_epoch
import mlflow
from src.plots import draw_label_pie_chart, draw_confusion_matrix
from src.torch_utils import get_accuracy
from src.train_utils import get_loss_function
import torch


def predict(trained_model, test_loader, device, params):
    optimizer = torch.optim.Adam(trained_model.parameters(), lr=params["learning_rate"])
    ls_func = get_loss_function(params,device)
    trained_model.eval()
    test_loss, predicted_list, raw_predicted_list, label_list, file_name_list = run_one_epoch(params,trained_model,
                                                                                              test_loader, optimizer,
                                                                                              ls_func, device,
                                                                                              train=False)

    print("test_loss:", test_loss)
    # print("raw_predicted_list", raw_predicted_list)
    # print("predicted_list[0]:", predicted_list[0])
    # print("label_list[0]:", label_list[0])
    mlflow.log_metric("test_loss", test_loss)
    draw_label_pie_chart(params["num_classes"], lambda: (t for t in predicted_list), params["benchmark"],
                         name="predicted-data")

    print("-" * 10)
    acc, flatten_predicted_list, flatten_label_list = get_accuracy(predicted_list, label_list)

    draw_confusion_matrix(flatten_predicted_list, flatten_label_list, params["num_classes"],params["benchmark"], name="predicted-"+params["task_type"],acc=acc)


    mlflow.log_metric("Predicted Accuracy", acc)
    print(f'Predicted Accuracy: {acc:.4f}')

    return predicted_list, raw_predicted_list, file_name_list, acc
