import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from torch.nn import Linear, BatchNorm1d, Embedding, ModuleList, LayerNorm, Dropout, ReLU, LeakyReLU, Identity, Tanh
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
    def get_default_hyperparameters(self):
        return {
            "embedding_size": 64,
            "num_gnn_layers": 2,
            "num_linear_layer": 2,
            "activation": "relu",
            "feature_size": 1,
            "dropout_probability": {"gnn_dropout_rate": 0, "mlp_dropout_rate": 0, "gnn_inner_layer_dropout_rate": 0},
            "use_intermediate_gnn_results": False,
            "message_normalization": False,
            "residual_every_num_layers": 0,
            "dense_every_num_layers": 0,
            "dense_intermediate_layer_activation_fn": Tanh(),
            "initial_node_representation_layer":False,
            "initial_node_representation_activation_fn": Tanh(),
            "linear_transformation_activation_fn":Tanh(),
            "inter_layer_norm": True,
            "regression_layer_norm":True
        }

    def __init__(self, label_size, vocabulary_size, edge_arity_dict, input_params):
        super().__init__()
        hyper_parameters = self.get_default_hyperparameters()
        hyper_parameters.update(input_params)

        self._use_intermediate_gnn_results = hyper_parameters["use_intermediate_gnn_results"]
        self._feature_size = hyper_parameters["feature_size"]
        self._embedding_size = hyper_parameters["embedding_size"]
        self._num_gnn_layers = hyper_parameters["num_gnn_layers"]
        self._num_linear_layer = hyper_parameters["num_linear_layer"]
        if self._feature_size > 1:
            self.linear_in = Linear(self._feature_size, self._embedding_size)
        self.embedding = Embedding(vocabulary_size, self._embedding_size)
        self._activation = hyper_parameters["activation"]
        self._dropout_probability = hyper_parameters["dropout_probability"]
        self._message_normalization = hyper_parameters["message_normalization"]
        self._residual_every_num_layers = hyper_parameters["residual_every_num_layers"]
        self._dense_every_num_layers = hyper_parameters["dense_every_num_layers"]
        self._dense_intermediate_layer_activation_fn = hyper_parameters["dense_intermediate_layer_activation_fn"]
        self._inter_layer_norm = hyper_parameters["inter_layer_norm"]
        self._regression_layer_norm = hyper_parameters["regression_layer_norm"]
        self._initial_node_representation_layer=hyper_parameters["initial_node_representation_layer"]

        if self._initial_node_representation_layer==True:
            self.initial_node_representation=Linear(self._embedding_size,self._embedding_size,bias=False)
            self.initial_node_representation_activation_fn=hyper_parameters["initial_node_representation_activation_fn"]

        # initialize conv layers
        self.hyper_conv_list = ModuleList()
        self.conv_norm_list = ModuleList()
        self.conv_act_list = ModuleList()
        self.conv_drop_list = ModuleList()
        self.conv_dense_layer_list = ModuleList()
        for layer_idx in range(self._num_gnn_layers):
            self.hyper_conv_list.append(
                HyperConv(self._embedding_size, self._embedding_size, edge_arity_dict=edge_arity_dict,
                          activation=self._activation,
                          inner_layer_dropout_rate=self._dropout_probability["gnn_inner_layer_dropout_rate"],
                          message_normalization=self._message_normalization))
            self.conv_norm_list.append(LayerNorm(self._embedding_size))
            self.conv_act_list.append(get_activation(self._activation))
            self.conv_drop_list.append(Dropout(p=self._dropout_probability["gnn_dropout_rate"]))
            if self._dense_every_num_layers!=0:
                if layer_idx % self._dense_every_num_layers == 0:
                    self.conv_dense_layer_list.append(Linear(self._embedding_size, self._embedding_size, bias=False))

        # transform concatenated intermediate layer to linear layer size, +1 means include embeddeding layer
        if self._use_intermediate_gnn_results==True:
            self.linear_transformation_for_intermediate_results = Linear(self._embedding_size * (self._num_gnn_layers + 1),
                                                                         self._embedding_size)
            self.linear_transformation_activation_fn= hyper_parameters["linear_transformation_activation_fn"]

        # initialize linear layers
        self.regression_linear_list, self.regression_linear_lin_norm_list, self.regression_linear_act_list, self.regression_linear_dropout_list = initialize_linear_layers(
            num_linear_layer=self._num_linear_layer, embedding_size=self._embedding_size, activation=self._activation,
            dropout_probability=self._dropout_probability["mlp_dropout_rate"], norm=self._regression_layer_norm)

        output_size = 1 if label_size == 2 else label_size
        self.regression_linear_out = Linear(self._embedding_size, output_size, bias=True)

    def forward(self, data):
        x, edge_index, target_indices, edge_list = \
            data.x, data.edge_index, data.target_indices, data.edge_list

        target_indices = torch.ravel(target_indices)

        if self._feature_size <= 1:
            x = torch.ravel(x)
            x = self.embedding(x)
        else:
            x = self.linear_in(x)


        # initial representation
        if self._initial_node_representation_layer == True:
            x = self.initial_node_representation(x)
            x = self.initial_node_representation_activation_fn(x)

        # output from each layer (including initial layer) and concatenate them in the end
        intermediate_layer_results = [x]

        #layer loop begins
        last_node_representations = x
        dense_layer_index = 0
        # GNN layers
        for layer_idx, (conv, conv_norm, conv_act, conv_drop) in enumerate(
                zip(self.hyper_conv_list, self.conv_norm_list, self.conv_act_list, self.conv_drop_list)):


            # Pass residuals through:
            if self._residual_every_num_layers != 0:
                if layer_idx % self._residual_every_num_layers == 0:
                    tmp = x
                    if layer_idx > 0:
                        x += last_node_representations
                        x /= 2
                    last_node_representations = tmp

            # Message passing
            x = conv(x, edge_index, edge_list)

            intermediate_layer_results.append(x)

            # todo:Global exchange

            # Layer normalize
            if self._inter_layer_norm == True:
                x = conv_norm(x)
                # x = conv_act(x)

            # Apply dense layer, if needed.
            if self._dense_every_num_layers!=0:
                if layer_idx % self._dense_every_num_layers == 0:
                    x = self.conv_dense_layer_list[dense_layer_index](x)
                    x = F.dropout(x, p=0, training=self.training)
                    x = self._dense_intermediate_layer_activation_fn(x)
                    dense_layer_index += 1

            # Dropout
            if self.training == True and layer_idx < len(
                    self.hyper_conv_list) - 1:  # don't dropout at last conv layer
                x = conv_drop(x)

        if self._use_intermediate_gnn_results == True:
            x = torch.concat(intermediate_layer_results, dim=1)
            x = torch.index_select(x, dim=0, index=target_indices)  # gather label node
            x = self.linear_transformation_for_intermediate_results(x)
            x = self.linear_transformation_activation_fn(x)

        else:
            x = torch.index_select(x, dim=0, index=target_indices)  # gather label node

        # linear layers
        x = forward_linear_layers(x, self.regression_linear_list, self.regression_linear_lin_norm_list, self.regression_linear_act_list,
                                  self.regression_linear_dropout_list, self.regression_linear_out, self.training, norm=self._regression_layer_norm)
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
