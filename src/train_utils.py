import torch
def get_loss_function(params):
    if params["task_type"] == "binary_classification" :
        loss_function = torch.nn.BCELoss()
    else:
        if len(params["class_weight"])==0:
            loss_function = torch.nn.CrossEntropyLoss()
        else:
            loss_function=torch.nn.CrossEntropyLoss(weight=torch.tensor(params["class_weight"]))
    return loss_function