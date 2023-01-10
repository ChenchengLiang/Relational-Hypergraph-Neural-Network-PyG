import torch
from torch_geometric.profile import count_parameters
def get_loss_function(params):
    if params["task_type"] == "binary_classification" :
        loss_function = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(params["class_weight"][1]*10))
        #loss_function = torch.nn.BCELoss(weight=torch.tensor(params["class_weight"][1]))
    else:
        if len(params["class_weight"])==0:
            loss_function = torch.nn.CrossEntropyLoss()
        else:
            loss_function=torch.nn.CrossEntropyLoss(weight=torch.tensor(params["class_weight"]))
    return loss_function

def get_parameter_summary(model):
    for name, param in model.named_parameters():
        print(name, param.shape)
    print("total parameters", sum(p.numel() for p in model.parameters()))
    print("trainable parameters", count_parameters(model))