from torch.nn import ReLU,LeakyReLU,Identity

def get_activation(activation):
    if activation == "relu":
        return ReLU()
    elif activation == "leak_relu":
        return LeakyReLU(negative_slope=0.2)
    else:
        return Identity()