from torch.nn import ReLU, LeakyReLU, Identity, Linear, LayerNorm, ModuleList, Tanh, Dropout
import numpy as np
from src.utils import manual_flatten
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


def initialize_linear_layers(num_linear_layer, embedding_size, activation, dropout_probability):
    linear_list = ModuleList()
    linear_lin_norm_list = ModuleList()
    linear_act_list = ModuleList()
    linear_dropout_list = ModuleList()
    for i in range(num_linear_layer):
        linear_list.append(Linear(embedding_size, embedding_size,bias=True))
        linear_lin_norm_list.append(LayerNorm(embedding_size))
        linear_act_list.append(get_activation(activation))
        linear_dropout_list.append(Dropout(p=dropout_probability))
    return linear_list, linear_lin_norm_list, linear_act_list,linear_dropout_list

def forward_linear_layers(x,linear_list,linear_ln_list,linear_act_list,linear_dropout_list,linear_out,training):
    for i, (lin, lin_norm, act, drop) in enumerate(
            zip(linear_list, linear_ln_list, linear_act_list, linear_dropout_list)):
        x = lin(x)
        x = lin_norm(x)
        if training == True and i < len(linear_list) - 1:  # don't dropout at last conv layer
            x = drop(x)  # x = F.dropout(x, p=0.8, training=self.training)
        x = act(x)

    x = linear_out(x)
    return x