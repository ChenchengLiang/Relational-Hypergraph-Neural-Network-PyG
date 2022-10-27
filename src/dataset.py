import torch
import torch_geometric
import numpy as np
from torch_geometric.data import Dataset, Data
from utils import get_file_list, unzip_file, read_one_filed
import os


class HornGraphDataset(Dataset):
    def __init__(self, root, params,transform=None, pre_transform=None, pre_filter=None):
        """
                root = Where the dataset should be stored. This folder is split
                """
        self.root = root
        self.num_classes = params["num_classes"]
        self.vocabulary = set()
        self.graph_type = params["graph_type"]
        self.learning_task=params["learning_task"]
        self.self_loop=params["self_loop"]
        super().__init__(root, transform, pre_transform, pre_filter)

    @property
    def raw_file_names(self):
        """ If this file exists in raw_dir, the download is not triggered.
            (The download func. is not implemented here)
        """
        return get_file_list(self.raw_dir, "." + self.graph_type + ".JSON")

    @property
    def processed_file_names(self):
        """ If these files are found in raw_dir, processing is skipped"""
        return ["data_" + str(i) + ".pt" for i, name in enumerate(self.raw_file_names)]

    def download(self):
        pass

    def process(self):
        self.vocabulary, token_map = self.build_vocabulary()

        file_list = self.raw_file_names
        for index, file_name in enumerate(file_list):
            ############################## read file begin##############################
            unzip_file(file_name)
            json_file_name = file_name[:-len(".zip")]
            node_symbol_list = read_one_filed(json_file_name, "nodeSymbolList")
            num_node=len(node_symbol_list)
            node_indices = list(range(num_node))

            #ASTEdge
            if self.graph_type == "hyperEdgeGraph":
                graph_edge_list = ["relationSymbolArgumentEdge","ASTLeftEdge", "ASTRightEdge", "guardEdge","quantifierEdge","binaryEdge",
                                   "controlFlowHyperEdge", "dataFlowHyperEdge", "ternaryHyperEdge"]
            else:
                graph_edge_list = ["relationSymbolArgumentEdge","relationSymbolInstanceEdge", "argumentInstanceEdge",
                                   "clauseHeadEdge","clauseBodyEdge", "clauseArgumentEdge","ASTLeftEdge", "ASTRightEdge", "guardEdge",
                                   "dataEdge","quantifierEdge","binaryEdge"]

            # form learning label according to the task
            target_indices, target_label, graph_edge_list = self._construct_learning_label_and_edges(json_file_name,
                                                                                                     graph_edge_list,
                                                                                                     node_indices)

            edge_list, edge_arity_dict = self._construct_edge_list(json_file_name, graph_edge_list,num_node)

            if os.path.exists(json_file_name):
                os.remove(json_file_name)
            ############################## read file end ##############################

            # template label and mask
            teamplate_node_mask = [True if i in target_indices else False for i in node_indices]

            # transform node features, edges, and labels to tensors
            node_features = self.tokenize_symbols(token_map, node_symbol_list, self.graph_type)
            x_tensor = torch.tensor([[n] for n in node_features], dtype=torch.long)
            target_indices_tensor = torch.tensor(target_indices, dtype=torch.long)
            y_tensor = torch.tensor(target_label)

            edge_list = [torch.tensor(edges, dtype=torch.long).t().contiguous() for edges in edge_list]

            data = Data(x=x_tensor,
                        edge_index=torch.tensor([[0, 0]]).t().contiguous(),
                        y=y_tensor,
                        teamplate_node_mask=teamplate_node_mask,
                        target_indices=target_indices_tensor,
                        edge_list=edge_list,
                        edge_arity_dict=edge_arity_dict,
                        file_name=file_name
                        )
            torch.save(data,
                       os.path.join(self.processed_dir,
                                    f'data_{index}.pt'))

    def len(self):
        return len(self.processed_file_names)

    def get(self, idx):
        data = torch.load(os.path.join(self.processed_dir, f'data_{idx}.pt'))
        return data


    def _construct_learning_label_and_edges(self,json_file_name,graph_edge_list,node_indices):
        if self.learning_task in ["template_binary_classification","template_multi_classification"]:
            target_indices = read_one_filed(json_file_name, "labelIndices")
            target_label = read_one_filed(json_file_name, "labelList")
            graph_edge_list = graph_edge_list + ["templateEdge"]
            graph_edge_list = graph_edge_list + ["templateASTEdge"]
        elif self.learning_task == "argument_binary_classification":
            target_indices = node_indices
            argument_indices = read_one_filed(json_file_name, "argumentIndices")
            target_label = [1 if i in argument_indices else 0 for i in node_indices]
        else:
            target_indices = node_indices
            target_label= [1]*len(node_indices)
        return target_indices,target_label,graph_edge_list



    def _construct_edge_list(self, json_file_name, edge_list_fields,num_node):
        binary_dummy_edge = [0, 0]
        tenary_dummy_edge = [0, 0, 0]
        edge_list = []
        edge_arity_dict = {}
        for feild in edge_list_fields:
            edges = read_one_filed(json_file_name, feild)
            # add dummy edge when the read edge is empty
            if len(edges) == 0:
                if feild in ["controlFlowHyperEdges", "dataFlowHyperEdges", "ternaryAdjacencyList"]:
                    edges = [tenary_dummy_edge]
                else:
                    edges = [binary_dummy_edge]
            edge_arity_dict[feild] = len(edges[0])
            edge_list.append(edges)

        if self.self_loop == True:
            slef_loop_edges = [[i, i] for i in range(num_node)]
            edge_list.append(slef_loop_edges)
            edge_arity_dict["selfLoopEdges"] = len(slef_loop_edges[0])

        return edge_list, edge_arity_dict

    def build_vocabulary(self):
        vocabulary_set = set(
            ["dummy", "unknown_node", "unknown_predicate", "unknown_symbolic_constant", "unknown_predicate_argument",
             "unknown_operator", "unknown_constant", "unknown_guard", "unknown_template", "unknown_predicateName",
             "unknown_clause", "unknown_clauseHead", "unknown_clauseBody", "unknown_clauseArgument"])

        for file_name in self.raw_file_names:
            unzip_file(file_name)
            json_file_name = file_name[:-len(".zip")]
            node_symbol_list = read_one_filed(json_file_name, "nodeSymbolList")
            vocabulary_set.update(node_symbol_list)
            if os.path.exists(json_file_name):
                os.remove(json_file_name)

        token_map = {}
        token_id = 0
        # todo: pad vocabulary_set

        vocabulary_set = set([self.convert_constant_to_category(w) for w in vocabulary_set])
        for word in sorted(vocabulary_set):
            token_map[word] = token_id
            token_id = token_id + 1
        # print("vocabulary_set",vocabulary_set)
        # print("token_map",token_map)
        return vocabulary_set, token_map

    def convert_constant_to_category(self, constant_string):
        converted_string = constant_string
        if constant_string.isdigit() and int(constant_string) > 1:
            converted_string = "positive_constant"
        elif converted_string[1:].isdigit() and int(constant_string) < -1:
            converted_string = "negative_constant"
        return converted_string

    def tokenize_symbols(self, token_map, node_symbols, graph_type):
        if graph_type == "hyperEdgeGraph":
            unknown_node_map = {"CONTROL": "unknown_predicate", "guard": "unknown_guard",
                                "predicateArgument": "unknown_predicate_argument", "template": "unknown_template",
                                "symbolicConstant": "unknown_symbolic_constant"}
        else:
            unknown_node_map = {"predicateArgument": "unknown_predicate_argument", "template": "unknown_template",
                                "symbolicConstant": "unknown_symbolic_constant",
                                "predicateName": "unknown_predicateName",
                                "clause": "unknown_clause",
                                "clauseHead": "unknown_clauseHead", "clauseBody": "unknown_clauseBody",
                                "clauseArgument": "unknown_clauseArgument"}

        converted_node_symbols = [self.convert_constant_to_category(word) for word in node_symbols]
        # node tokenization
        full_operator_list = ["+", "-", "*", "/", ">", ">0", ">=", ">=0", "=", "=0", "<", "<0", "<=", "<=0", "==",
                              "==0", "===", "!", "+++", "++", "**", "***",
                              "--", "---", "=/=", "&", "|", "EX", "and", "or", "eps"]
        tokenized_node_label_ids = []
        # print("node_symbols",node_symbols)
        # print("converted_node_symbols", converted_node_symbols)
        # print("token_map", token_map)
        for symbol in converted_node_symbols:
            if symbol in token_map:
                tokenized_node_label_ids.append(token_map[symbol])
            # elif "CONTROL" in symbol:
            #     tokenized_node_label_ids.append(token_map["unknown_predicate"])
            elif symbol.isnumeric() or symbol[1:].isnumeric():
                tokenized_node_label_ids.append(token_map["unknown_constant"])
            elif symbol in full_operator_list:
                tokenized_node_label_ids.append(token_map["unknown_operator"])
            else:
                temp_flag = 0
                for k in unknown_node_map:
                    if k + "_" in symbol:
                        temp_flag = 1
                        # print(k)
                        tokenized_node_label_ids.append(token_map[unknown_node_map[k]])
                if temp_flag == 0:
                    # print("node_symbols",symbol)
                    tokenized_node_label_ids.append(token_map["unknown_node"])
        return tokenized_node_label_ids
