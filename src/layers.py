import torch
from torch.nn import Linear, Parameter,ModuleList,Sequential,ReLU,BatchNorm1d,LayerNorm,LeakyReLU,Identity
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree
from torch import Tensor
import torch.nn.functional as F
from src.torch_utils import get_activation
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
class HyperConv(MessagePassing):
    def __init__(self, in_channels, out_channels, edge_arity_dict,activation="relu"):
        super().__init__()
        self.embedding_size=in_channels
        self.edge_arity_dict=edge_arity_dict
        self.activation=activation
        self.negative_slope: float = 0.2


        self.linear_layers, self.linear_layers_ln,self.linear_layers_act= self._get_linear_layers()

        self.final_update_func=get_activation(self.activation)


        self.reset_parameters()

    def reset_parameters(self):
        for i,_ in enumerate(self.linear_layers):
            self.linear_layers[i].reset_parameters()

    def forward(self, x, edge_index,edge_list):
        # x has shape [N, in_channels]
        # element in edge_list has shape [edge_arity, E]

        aggregated_messages = torch.zeros(len(x),self.embedding_size).to(device)#[N, embedding_size]
        linear_layer_counter=0
        for edges in edge_list:
            edge_arity=len(edges)
            # Step 1: concatenate neighbors
            node_features_in_edge_columns=[]
            for position in range(edge_arity):
                position_edge_index=edges[position, :]
                #print("position_edge_index",len(position_edge_index),position_edge_index)
                gathered_nodes = torch.index_select(x, dim=0, index=position_edge_index)
                node_features_in_edge_columns.append(gathered_nodes)
            concatednated_node_features=torch.concat(node_features_in_edge_columns,dim=-1).to(device) #[E, embedding_size*2]
            #print("concatednated_node_features.shape",concatednated_node_features.shape)

            # Step 2: Linearly transform concatenated neighbors and add to messages.
            for position in range(edge_arity):
                #compute messages
                message_per_position = self.linear_layers[linear_layer_counter](concatednated_node_features) #[E, embedding_size]
                #normalization
                message_per_position=self.linear_layers_ln[linear_layer_counter](message_per_position)
                message_per_position = self.linear_layers_act[linear_layer_counter](message_per_position)
                # message_per_position = F.dropout(message_per_position, p=0.8, training=self.training)


                #add messages to every target node position
                target_node_index = edges[position, :] #[E]
                aggregated_messages=aggregated_messages.index_add_(0,target_node_index,message_per_position) #[N,embedding_size]

                linear_layer_counter = linear_layer_counter + 1

        #aggregated_messages=F.relu(aggregated_messages) #[N,embedding_size]
        aggregated_messages = self.final_update_func(aggregated_messages)

        # Start propagating messages.
        #out = self.propagate(edge_index, x=x,message=aggregated_messages)
        out = aggregated_messages
        return out

    def _get_linear_layers(self):
        linear_layers=ModuleList()
        linear_layers_ln=ModuleList()
        linear_layers_act=ModuleList()
        for k in self.edge_arity_dict:
            for _ in range(self.edge_arity_dict[k]):
                linear_layers.append(Linear(self.embedding_size * self.edge_arity_dict[k], self.embedding_size,bias=False))
                linear_layers_ln.append(LayerNorm(self.embedding_size))
                linear_layers_act.append(get_activation(self.activation))
        return linear_layers,linear_layers_ln,linear_layers_act


    # def message(self, x_i,x_j,message):
    #     # x_j has shape [E, out_channels]
    #
    #     return message

