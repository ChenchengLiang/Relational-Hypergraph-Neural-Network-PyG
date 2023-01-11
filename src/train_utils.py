import torch
from torch_geometric.profile import count_parameters
def get_loss_function(params,device):
    if params["task_type"] == "binary_classification" :
        loss_function = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(params["class_weight"][1]*10)).to(device)
        #, pos_weight=torch.tensor(params["class_weight"][1]*10)
        #loss_function = torch.nn.functional.binary_cross_entropy_with_logits
        #loss_function = torch.nn.BCELoss(weight=torch.tensor(params["class_weight"][1])).to(device)
    else:
        # todo: use alternative to tf.nn.sigmoid_cross_entropy_with_logits
        if len(params["class_weight"])==0:
            loss_function = torch.nn.CrossEntropyLoss().to(device)
        else:
            loss_function=torch.nn.CrossEntropyLoss(weight=torch.tensor(params["class_weight"])).to(device)
    return loss_function

def get_parameter_summary(model):
    def _get_param_num(param):
        num=0
        if len(param.shape) == 1:
            num += param.shape[0]
        else:
            num += param.shape[0] * param.shape[1]
        return num
    embedding=0
    conv=0
    regression=0
    for name, param in model.named_parameters():
        #print(name, param.shape)
        if "embedding" in name:
            embedding=param.shape[0]*param.shape[1]
        if "conv" in name:
            conv+=_get_param_num(param)
        if "regression" in name:
            regression += _get_param_num(param)


    print("embedding:",embedding)
    print("conv:", conv)
    print("regression:",regression)
    print("total parameters", embedding+conv+regression)
    print("trainable parameters", count_parameters(model))