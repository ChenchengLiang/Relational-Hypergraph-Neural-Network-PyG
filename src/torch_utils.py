from torch.nn import ReLU, LeakyReLU, Identity, Linear, LayerNorm, ModuleList, Tanh
import numpy as np
from utils import manual_flatten
import torch
def get_accuracy(predicted_list,label_list):
    flatten_predicted_list = np.array(manual_flatten(predicted_list)).ravel()
    flatten_label_list = np.array(manual_flatten(label_list)).ravel()

    correct = (flatten_predicted_list == flatten_label_list).sum()
    acc = int(correct) / len(flatten_label_list)
    return acc,flatten_predicted_list,flatten_label_list

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
    linear_list = ModuleList()
    linear_ln_list = ModuleList()
    linear_act_list = ModuleList()
    for i in range(num_linear_layer):
        linear_list.append(Linear(embedding_size, embedding_size))
        linear_ln_list.append(LayerNorm(embedding_size))
        linear_act_list.append(get_activation(activation))
    return linear_list, linear_ln_list, linear_act_list

