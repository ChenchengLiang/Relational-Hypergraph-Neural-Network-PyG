import torch
def get_loss_function(task_type,class_weight):
    if task_type == "binary_classification" :
        loss_function = torch.nn.BCELoss()
    else:
        loss_function=torch.nn.CrossEntropyLoss(weight=torch.tensor(class_weight))
    return loss_function