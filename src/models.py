import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch.nn import Linear, BatchNorm1d, Embedding, ModuleList, LayerNorm, Dropout, ReLU, LeakyReLU, Identity
from torch_utils import get_activation, initialize_linear_layers
from layers import HyperConv


class GNN_classification(torch.nn.Module):
    def __init__(self, label_size, vocabulary_size, embedding_size, num_gnn_layers, num_linear_layer, activation):
        super().__init__()
        embedding_size = embedding_size

        self.embedding = Embedding(vocabulary_size, embedding_size)

        # initialize conv layers
        conv_list = []
        conv_ln_list = []
        conv_act_list = []
        for i in range(num_gnn_layers):
            conv_list.append(GCNConv(embedding_size, embedding_size))
            conv_ln_list.append(LayerNorm(embedding_size))
            conv_act_list.append(activation)
        self.conv_list = ModuleList(conv_list)
        self.conv_ln_list = ModuleList(conv_ln_list)
        self.conv_act_list = ModuleList(conv_act_list)

        # initialize linear layers
        self.linear_list, self.linear_ln_list, self.linear_act_list = initialize_linear_layers(
            num_linear_layer=num_linear_layer, embedding_size=embedding_size, activation=activation)

        output_size = 1 if label_size == 2 else label_size
        self.linear_out = Linear(embedding_size, output_size)

    def forward(self, data):
        x, edge_index, teamplate_node_mask, target_indices, edge_list = \
            data.x, data.edge_index, data.teamplate_node_mask, data.target_indices, data.edge_list
        x = torch.ravel(x)

        target_indices = torch.ravel(target_indices)

        x = self.embedding(x)

        edges = edge_list[0]

        # GNN layers
        for conv, ln, act in zip(self.conv_list, self.conv_ln_list,self.conv_act_list):
            x = conv(x, edges)
            x = ln(x)
            # x = F.dropout(x, p=0.8, training=self.training)
            x = act(x)

        # x = x[teamplate_node_mask]
        # gather template node
        x = torch.index_select(x, dim=0, index=target_indices)

        # linear layers
        for lin, ln, act in zip(self.linear_list, self.linear_ln_list, self.linear_act_list):
            x = lin(x)
            x = ln(x)
            # x = F.dropout(x, p=0.8, training=self.training)
            x = act(x)

        x = self.linear_out(x)
        return x


class Hyper_classification(torch.nn.Module):
    def __init__(self, label_size, vocabulary_size, edge_arity_dict, embedding_size, num_gnn_layers,
                 num_linear_layer, activation):
        super().__init__()
        embedding_size = embedding_size

        self.embedding = Embedding(vocabulary_size, embedding_size)
        self.activation = activation

        # initialize conv layers
        hyper_conv_list = []
        conv_ln_list = []
        conv_act_list = []
        for i in range(num_gnn_layers):
            hyper_conv_list.append(
                HyperConv(embedding_size, embedding_size, edge_arity_dict=edge_arity_dict, activation=self.activation))
            conv_ln_list.append(LayerNorm(embedding_size))
            conv_act_list.append(get_activation(self.activation))
        self.hyper_conv_list = ModuleList(hyper_conv_list)
        self.conv_ln_list = ModuleList(conv_ln_list)
        self.conv_act_list = ModuleList(conv_act_list)

        # initialize linear layers
        self.linear_list, self.linear_ln_list, self.linear_act_list = initialize_linear_layers(
            num_linear_layer=num_linear_layer, embedding_size=embedding_size, activation=activation)

        output_size = 1 if label_size == 2 else label_size
        self.linear_out = Linear(embedding_size, output_size)

    def forward(self, data):
        x, edge_index, teamplate_node_mask, target_indices, edge_list = \
            data.x, data.edge_index, data.teamplate_node_mask, data.target_indices, data.edge_list

        x = torch.ravel(x)
        target_indices = torch.ravel(target_indices)

        # embedding layer
        x = self.embedding(x)

        # GNN layers
        for conv, ln, act in zip(self.hyper_conv_list, self.conv_ln_list, self.conv_act_list):
            x = conv(x, edge_index, edge_list)
            x = ln(x)
            # x = F.dropout(x, p=0.8, training=self.training)
            x = act(x)

        # gather template node
        # x = x[teamplate_node_mask]
        x = torch.index_select(x, dim=0, index=target_indices)

        # linear layers
        for lin, ln, act in zip(self.linear_list, self.linear_ln_list, self.linear_act_list):
            x = lin(x)
            x = ln(x)
            # x = F.dropout(x, p=0.8, training=self.training)
            x = act(x)

        x = self.linear_out(x)
        return x


class Full_connected_model(torch.nn.Module):
    def __init__(self, label_size, vocabulary_size, embedding_size):
        super().__init__()
        embedding_size = embedding_size
        self.embedding = Embedding(vocabulary_size, embedding_size)
        self.linear0 = Linear(embedding_size, embedding_size)
        self.linear1 = Linear(embedding_size, embedding_size)
        self.linear2 = Linear(embedding_size, embedding_size)

        output_size = 1 if label_size == 2 else label_size
        self.linear_out = Linear(embedding_size, output_size)

        self.bn0 = BatchNorm1d(embedding_size)
        self.bn1 = BatchNorm1d(embedding_size)
        self.bn2 = BatchNorm1d(embedding_size)

    def forward(self, data):
        x, edge_index, teamplate_node_mask, target_indices, edge_list = \
            data.x, data.edge_index, data.teamplate_node_mask, data.target_indices, data.edge_list

        x = torch.ravel(x)
        x = self.embedding(x)

        x = self.linear0(x)
        x = self.bn0(x)
        x = F.relu(x)

        # x = x[teamplate_node_mask]
        x = torch.index_select(x, dim=0, index=target_indices)

        x = self.linear1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.linear2(x)
        x = self.bn2(x)
        x = F.relu(x)

        x = self.linear_out(x)
        return x
