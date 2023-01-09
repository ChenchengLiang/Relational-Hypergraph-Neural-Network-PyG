import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from torch.nn import Linear, BatchNorm1d, Embedding, ModuleList, LayerNorm, Dropout, ReLU, LeakyReLU, Identity
from src.torch_utils import get_activation, initialize_linear_layers, forward_linear_layers
from src.layers import HyperConv


class GNN_classification(torch.nn.Module):
    def __init__(self, label_size, vocabulary_size, edge_arity_dict, embedding_size, num_gnn_layers, num_linear_layer,
                 activation, gnn=GCNConv, feature_size=1, drop_out_probability=0):
        super().__init__()
        self.embedding_size = embedding_size
        self.drop_out_probability = drop_out_probability
        self.feature_size = feature_size
        self.linear_in = Linear(feature_size, embedding_size)
        self.embedding = Embedding(vocabulary_size, embedding_size)
        self._edge_arity_dict = edge_arity_dict

        # initialize conv layers
        self.conv_list = ModuleList()
        self.conv_ln_list = ModuleList()
        self.conv_act_list = ModuleList()
        self.conv_drop_list = ModuleList()
        for i in range(num_gnn_layers):
            self.conv_list.append(gnn(embedding_size, embedding_size))
            self.conv_ln_list.append(LayerNorm(embedding_size))
            self.conv_act_list.append(get_activation(activation))
            self.conv_drop_list.append(Dropout(self.drop_out_probability))

        # initialize linear layers
        self.linear_list, self.linear_ln_list, self.linear_act_list, self.linear_dropout_list = initialize_linear_layers(
            num_linear_layer=num_linear_layer, embedding_size=embedding_size, activation=activation,
            dropout_probability=drop_out_probability)

        output_size = 1 if label_size == 2 else label_size
        self.linear_out = Linear(embedding_size, output_size)

    def forward(self, data):
        x, edge_index, edge_list, target_indices = data.x, data.edge_index, data.edge_list, data.target_indices

        target_indices = torch.ravel(target_indices)

        if self.feature_size <= 1:
            x = torch.ravel(x)
            x = self.embedding(x)
        else:
            x = self.linear_in(x)

        # use global binary edge as edge index
        for i, (edge, edge_dict_key) in enumerate(zip(edge_list, self._edge_arity_dict)):
            if edge_dict_key == "binaryEdge":
                edges = edge_list[i]

        # GNN layers
        for conv, ln, act, drop in zip(self.conv_list, self.conv_ln_list, self.conv_act_list, self.conv_drop_list):
            x = conv(x, edges)
            x = ln(x)
            x = act(x)
            if self.training == True:
                x = drop(x)

        # x = x[teamplate_node_mask]
        # gather template node
        x = torch.index_select(x, dim=0, index=target_indices)

        # linear layers
        x = forward_linear_layers(x, self.linear_list, self.linear_ln_list, self.linear_act_list,
                                  self.linear_dropout_list, self.linear_out, self.training)
        return x


class Hyper_classification(torch.nn.Module):
    def __init__(self, label_size, vocabulary_size, edge_arity_dict, embedding_size, num_gnn_layers,
                 num_linear_layer, activation, feature_size=1,
                 dropout_probability={"gnn_dropout_rate": 0, "mlp_dropout_rate": 0},
                 use_intermediate_gnn_results=False,message_normalization=False):
        super().__init__()
        self.use_intermediate_gnn_results = use_intermediate_gnn_results
        self.feature_size = feature_size
        self.embedding_size = embedding_size
        self.linear_in = Linear(feature_size, embedding_size)
        self.embedding = Embedding(vocabulary_size, embedding_size)
        self.activation = activation
        self.dropout_probability = dropout_probability
        self.message_normalization = message_normalization

        # initialize conv layers
        self.hyper_conv_list = ModuleList()
        self.conv_norm_list = ModuleList()
        self.conv_act_list = ModuleList()
        self.conv_drop_list = ModuleList()
        for i in range(num_gnn_layers):
            self.hyper_conv_list.append(
                HyperConv(embedding_size, embedding_size, edge_arity_dict=edge_arity_dict, activation=self.activation,
                          inner_layer_dropout_rate=self.dropout_probability["gnn_inner_layer_dropout_rate"],message_normalization=self.message_normalization))
            self.conv_norm_list.append(LayerNorm(embedding_size))
            self.conv_act_list.append(get_activation(self.activation))
            self.conv_drop_list.append(Dropout(p=self.dropout_probability["gnn_dropout_rate"]))

        # transform concatenated intermediate layer to linear layer size, +1 means include embeddeding layer
        self.linear_transformation_for_intermediate_results = Linear(embedding_size * (num_gnn_layers + 1),
                                                                     embedding_size)

        # initialize linear layers
        self.linear_list, self.linear_lin_norm_list, self.linear_act_list, self.linear_dropout_list = initialize_linear_layers(
            num_linear_layer=num_linear_layer, embedding_size=embedding_size, activation=activation,
            dropout_probability=self.dropout_probability["mlp_dropout_rate"])

        output_size = 1 if label_size == 2 else label_size
        self.linear_out = Linear(embedding_size, output_size, bias=True)

    def forward(self, data):
        x, edge_index, target_indices, edge_list = \
            data.x, data.edge_index, data.target_indices, data.edge_list

        target_indices = torch.ravel(target_indices)

        if self.feature_size <= 1:
            x = torch.ravel(x)
            x = self.embedding(x)
        else:
            x = self.linear_in(x)

        # output from each layer (including embedding layer) and concatenate them in the end
        intermediate_layer_results = [x]
        # GNN layers
        for i, (conv, conv_norm, conv_act, conv_drop) in enumerate(
                zip(self.hyper_conv_list, self.conv_norm_list, self.conv_act_list, self.conv_drop_list)):
            x = conv(x, edge_index, edge_list)
            x = conv_norm(x)
            x = conv_act(x)
            if self.training == True and i < len(self.hyper_conv_list) - 1:  # don't dropout at last conv layer
                x = conv_drop(x)
            intermediate_layer_results.append(x)

        if self.use_intermediate_gnn_results == True:
            x = torch.concat(intermediate_layer_results, dim=1)
            x = torch.index_select(x, dim=0, index=target_indices)  # gather label node
            x = self.linear_transformation_for_intermediate_results(x)
        else:
            x = torch.index_select(x, dim=0, index=target_indices)  # gather label node

        # linear layers
        x = forward_linear_layers(x, self.linear_list, self.linear_lin_norm_list, self.linear_act_list,
                                  self.linear_dropout_list, self.linear_out, self.training)
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
