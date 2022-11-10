import torch
import numpy as np
import torch.nn.functional as F
from plots import loss_plot
import mlflow.pytorch
from tqdm import tqdm
import mlflow
from torch_utils import get_accuracy
from train_utils import get_loss_function


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Specify tracking server
mlflow.set_tracking_uri("http://localhost:5000")

def run_one_epoch(model,data_loader,optimizer,ls_func,train=True,task_type="binary_classification"):
    running_loss=0.0
    raw_predicted_list=[]
    predicted_list=[]
    label_list=[]
    file_name_list=[]
    for batch in data_loader:
        if type(batch) is list:
            batch=batch[0]
        batch.to(device) # Use GPU
        pred = model(batch)
        if task_type == "binary_classification":
            sigmoid_pred=torch.sigmoid(pred)
            raw_predicted_list.append(sigmoid_pred.cpu().detach().numpy())
            predicted_list.append(np.rint(sigmoid_pred.cpu().detach().numpy()))
            loss = ls_func(torch.squeeze(sigmoid_pred), batch.y.float())
        elif task_type == "multi_classification":
            softmax_value=torch.softmax(pred,dim=1).cpu().detach().numpy()
            raw_predicted_list.append(softmax_value)
            predicted_list.append(np.array([np.argmax(v) for v in softmax_value]))
            loss = ls_func(pred, batch.y)
            # print("softmax_value",softmax_value)
            # print([np.argmax(v) for v in softmax_value])
        else:
            pred = torch.squeeze(pred)
            raw_predicted_list.append(pred.cpu().detach().numpy())
            predicted_list.append(np.rint(pred.cpu().detach().numpy()))
            loss = ls_func(pred, batch.y)

        label_list.append(batch.y.cpu().detach().numpy())
        file_name_list.append(batch.file_name)
        # print("pred",len(pred),pred)
        # print("true_y",len(true_y),batch.y)
        running_loss += loss.cpu().detach().numpy()
        optimizer.zero_grad()  # Reset gradients
        if train==True:
            loss.backward() # calculate current gradients for every parameters
            optimizer.step() # update parameters based on current gradients
    return running_loss/len(data_loader),predicted_list,raw_predicted_list,label_list,file_name_list

def train(train_loader,valid_loader,model,params):
    ls_func = get_loss_function(params).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=params["learning_rate"], weight_decay=params["learning_rate"]*0.1)
    #optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    train_loss_list=[]
    valid_loss_list=[]
    best_loss=10000000
    best_epoch=0
    for epoch in tqdm(range(params["epochs"]),desc="Training progress"):
        #training
        model.train()
        train_loss,predicted_list,raw_predicted_list,label_list,file_name_list=run_one_epoch(model,train_loader,optimizer,ls_func,train=True,task_type=params["task_type"])
        train_loss_list.append(train_loss)
        mlflow.log_metric("train_loss",train_loss,epoch)


        #validating
        model.eval()
        valid_loss,predicted_list,raw_predicted_list,label_list,file_name_list=run_one_epoch(model,valid_loader,optimizer,ls_func,train=False,task_type=params["task_type"])
        valid_loss_list.append(valid_loss)
        mlflow.log_metric("valid_loss", valid_loss, epoch)
        valid_acc, flatten_predicted_list, flatten_label_list = get_accuracy(predicted_list, label_list)
        mlflow.log_metric("valid accuracy", valid_acc, epoch)

        if valid_loss<best_loss:
            best_loss=valid_loss
            best_epoch=epoch
            torch.save(model, '../models/best_model.pth')

        if valid_acc == 1:
            torch.save(model, '../models/best_model.pth')
            loss_plot(train_loss_list, valid_loss_list)
            mlflow.log_metric("early stop epoch",epoch)
            return model, optimizer

        if epoch % 50 == 0 or epoch == params["epochs"]-1:
            print("epoch:",epoch,"train_loss:",train_loss,"valid_loss:", valid_loss)

    print("best_epoch", best_epoch, "best_loss", best_loss)
    loss_plot(train_loss_list,valid_loss_list)
    return model,optimizer
