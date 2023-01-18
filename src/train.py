import os

import torch
import numpy as np
from src.plots import train_valid_plot, draw_confusion_matrix
from src.utils import make_dirct
import mlflow.pytorch
from tqdm import tqdm
import mlflow
from src.torch_utils import get_accuracy
from src.train_utils import get_loss_function


# import wandb


def run_one_epoch(params, model, data_loader, optimizer, ls_func, device, train=True):
    running_loss = 0.0
    raw_predicted_list = []
    predicted_list = []
    label_list = []
    file_name_list = []
    for batch in data_loader:
        if type(batch) is list:
            batch = batch[0]
        batch.to(device)  # Use GPU
        try:

            pred = model(batch)
            if params["task_type"] == "binary_classification":
                loss = ls_func(torch.squeeze(pred), batch.y.float(),
                               pos_weight=torch.tensor(params["class_weight"][1] * 10))
                sigmoid_pred = torch.sigmoid(pred)
                raw_predicted_list.append(sigmoid_pred.cpu().detach().numpy())
                predicted_list.append(np.rint(sigmoid_pred.cpu().detach().numpy()))

            elif params["task_type"] == "multi_classification":
                loss = ls_func(pred, batch.y)
                softmax_value = torch.softmax(pred, dim=1).cpu().detach().numpy()
                raw_predicted_list.append(softmax_value)
                predicted_list.append(np.array([np.argmax(v) for v in softmax_value]))
                # print("softmax_value",softmax_value)
                # print([np.argmax(v) for v in softmax_value])
            else:
                pred = torch.squeeze(pred)
                raw_predicted_list.append(pred.cpu().detach().numpy())
                predicted_list.append(np.rint(pred.cpu().detach().numpy()))
                loss = ls_func(pred, batch.y)
        except Exception as e:
            print(e)
            print("bug", batch["file_name"])

        label_list.append(batch.y.cpu().detach().numpy())
        file_name_list.append(batch.file_name)
        # print("pred",len(pred),pred)
        # print("true_y",len(true_y),batch.y)
        running_loss += loss.cpu().detach().numpy()
        optimizer.zero_grad()  # Reset gradients
        if train == True:
            loss.backward()  # calculate current gradients for every parameters
            if params["gradient_clip"] == True:
                # nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0, norm_type=2) # Gradient Norm Clipping
                torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=1.0)  # Gradient Value Clipping

            optimizer.step()  # update parameters based on current gradients
    return running_loss / len(data_loader), predicted_list, raw_predicted_list, label_list, file_name_list


def train(train_loader, valid_loader, model, device, params):
    ls_func = get_loss_function(params, device)
    model_folder = make_dirct(os.path.join(params["benchmark"], "model"))

    optimizer = torch.optim.Adam(model.parameters(), lr=params["learning_rate"])
    # optimizer = torch.optim.SGD(model.parameters(), lr=params["learning_rate"])
    # scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

    train_loss_list = []
    valid_loss_list = []
    train_acc_list = []
    valid_acc_list = []
    best_loss = 10000000
    best_epoch = 0
    for epoch in tqdm(range(params["epochs"]), desc="Training progress"):
        # training
        model.train()
        train_loss, predicted_list, raw_predicted_list, label_list, file_name_list = run_one_epoch(params, model,
                                                                                                   train_loader,
                                                                                                   optimizer, ls_func,
                                                                                                   device,
                                                                                                   train=True)
        train_loss_list.append(train_loss)
        mlflow.log_metric("train_loss", train_loss, epoch)
        train_acc, flatten_predicted_list, flatten_label_list = get_accuracy(predicted_list, label_list)
        train_acc_list.append(train_acc)
        mlflow.log_metric("train accuracy", '{:e}'.format(train_acc), epoch)

        # scheduler.step()

        # validating
        model.eval()
        valid_loss, predicted_list, raw_predicted_list, label_list, file_name_list = run_one_epoch(params, model,
                                                                                                   valid_loader,
                                                                                                   optimizer, ls_func,
                                                                                                   device,
                                                                                                   train=False)
        valid_loss_list.append(valid_loss)
        mlflow.log_metric("valid_loss", valid_loss, epoch)
        valid_acc, flatten_predicted_list, flatten_label_list = get_accuracy(predicted_list, label_list)
        valid_acc_list.append(valid_acc)
        mlflow.log_metric("valid accuracy", '{:e}'.format(valid_acc), epoch)
        mlflow.log_metric("epoch", epoch, epoch)

        if valid_loss <= best_loss:
            best_loss = valid_loss
            best_epoch = epoch
            torch.save(model, os.path.join(model_folder, "best_model.pth"))
            draw_confusion_matrix(flatten_predicted_list, flatten_label_list, params["num_classes"],
                                  params["benchmark"], name="best-valid-" + params["task_type"], acc=valid_acc)

        if valid_acc == 1.0:
            torch.save(model, os.path.join(model_folder, "best_model.pth"))
            mlflow.log_metric("early stop epoch", epoch)
            train_valid_plot(train_loss_list, valid_loss_list, params["benchmark"], field="loss")
            train_valid_plot(train_acc_list, valid_acc_list, params["benchmark"], field="acc")
            return model

        if epoch - best_epoch >= params["patient"]:
            torch.save(model, os.path.join(model_folder, "best_model.pth"))
            mlflow.log_metric("early stop epoch", epoch)
            train_valid_plot(train_loss_list, valid_loss_list, params["benchmark"], field="loss")
            train_valid_plot(train_acc_list, valid_acc_list, params["benchmark"], field="acc")
            return model

        if epoch % 50 == 0 or epoch == params["epochs"] - 1:
            print("epoch:", epoch, "train_loss:", train_loss, "valid_loss:", valid_loss)

    # wandb.log({"train_loss": train_loss,"valid_loss":valid_loss,"valid_acc":valid_acc,"early stop epoch":epoch,"epoch":epoch})
    print("best_epoch", best_epoch, "best_loss", best_loss)
    train_valid_plot(train_loss_list, valid_loss_list, params["benchmark"], field="loss")
    train_valid_plot(train_acc_list, valid_acc_list, params["benchmark"], field="acc")
    return model
