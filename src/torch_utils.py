from torch.nn import ReLU, LeakyReLU, Identity, Linear, LayerNorm, ModuleList, Tanh


def get_activation(activation):
    if activation == "relu":
        return ReLU()
    elif activation == "leak_relu":
        return LeakyReLU(negative_slope=0.2)
    elif activation == "tanh":
        return Tanh()
    else:
        return Identity()


def initialize_linear_layers(num_linear_layer, embedding_size, activation):
    linear_list = []
    linear_ln_list = []
    linear_act_list = []
    for i in range(num_linear_layer):
        linear_list.append(Linear(embedding_size, embedding_size))
        linear_ln_list.append(LayerNorm(embedding_size))
        linear_act_list.append(get_activation(activation))
    return ModuleList(linear_list), ModuleList(linear_ln_list), ModuleList(linear_act_list)
