import torch
from torch_geometric.data import Dataset, Data
from src.utils import get_file_list, unzip_file, read_one_filed, convert_constant_to_category
import os
from tqdm import tqdm


class HornGraphDataset(Dataset):
    def __init__(self, root, params, token_map, transform=None, pre_transform=None, pre_filter=None):
        """
                root = Where the dataset should be stored. This folder is split
                """
        self.root = root
        self.num_classes = params["num_classes"]
        self.token_map = token_map
        self.graph_type = params["graph_type"]
        self.learning_task = params["learning_task"]
        self._add_self_loop = params["add_self_loop_edges"]
        self._add_backward_edges = params["add_backward_edges"]
        self._add_global_edges = params["add_global_edges"]
        self._edge_types = params["edge_types"]
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

        file_list = self.raw_file_names
        for index, file_name in tqdm(enumerate(file_list), desc=os.path.basename(self.root)):
            ############################## read file begin##############################
            unzip_file(file_name)
            json_file_name = file_name[:-len(".zip")]
            node_symbol_list = read_one_filed(json_file_name, "nodeSymbolList")
            num_node = len(node_symbol_list)
            node_indices = list(range(num_node))

            # ASTEdge
            if self.graph_type == "hyperEdgeGraph":
                graph_edge_list = ["relationSymbolArgumentEdge", "ASTLeftEdge", "ASTRightEdge", "ASTEdge", "guardEdge",
                                   "quantifierEdge",
                                   "controlFlowHyperEdge", "dataFlowHyperEdge"]
            else:
                graph_edge_list = ["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
                                   "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge", "ASTLeftEdge",
                                   "ASTRightEdge", "ASTEdge", "guardEdge", "dataEdge",
                                   "quantifierEdge"
                                   ]

            # form learning label according to the task
            target_indices, target_label, graph_edge_list = self._construct_learning_label_and_edges(json_file_name,
                                                                                                     graph_edge_list,
                                                                                                     node_indices)

            edge_list, edge_arity_dict = self._construct_edge_list(json_file_name, graph_edge_list, num_node)

            if os.path.exists(json_file_name):
                os.remove(json_file_name)
            ############################## read file end ##############################

            # template label and mask
            teamplate_node_mask = [True if i in target_indices else False for i in node_indices]

            # transform node features, edges, and labels to tensors
            node_features = self.tokenize_symbols(self.token_map, node_symbol_list, self.graph_type)
            x_tensor = torch.tensor([[n] for n in node_features], dtype=torch.long)
            target_indices_tensor = torch.tensor(target_indices, dtype=torch.long)
            y_tensor = torch.tensor(target_label)

            data = Data(x=x_tensor,
                        edge_index=torch.tensor([[0, 0]]).t().contiguous(),
                        y=y_tensor,
                        teamplate_node_mask=teamplate_node_mask,
                        target_indices=target_indices_tensor,
                        edge_list=edge_list,
                        edge_arity_dict=edge_arity_dict,
                        file_name=file_name,
                        )
            torch.save(data,
                       os.path.join(self.processed_dir,
                                    f'data_{index}.pt'))

    def len(self):
        return len(self.processed_file_names)

    def get(self, idx):
        data = torch.load(os.path.join(self.processed_dir, f'data_{idx}.pt'))
        self._process_edge_list(data)
        return data

    def _process_edge_list(self, data):
        # todo:control all edge type here
        temp_edge_list=[]
        temp_edge_arity_dict={}
        for i, (edges, edge_dict_key) in enumerate(zip(data["edge_list"], data["edge_arity_dict"])):
            if edge_dict_key in self._edge_types:
                temp_edge_list.append(edges)
                temp_edge_arity_dict[edge_dict_key]=data["edge_arity_dict"][edge_dict_key]

        if self._add_self_loop == True:
            slef_loop_edges = [[i, i] for i in range(len(data["x"]))]
            temp_edge_list.append(slef_loop_edges)
            temp_edge_arity_dict["selfLoopEdges"] = len(slef_loop_edges[0])
        if self._add_backward_edges == True:
            # todo could add backward edge as new edge type
            for i, (edges, edge_dict_key) in enumerate(zip(temp_edge_list, temp_edge_arity_dict)):
                if len(edges[0]) == 2 and edge_dict_key != "selfLoopEdges":
                    backward_edges = [[edge[1], edge[0]] for edge in edges]
                    temp_edge_list[i] = edges + backward_edges
        if self._add_global_edges == True:
            binary_global_edges = []
            ternary_global_edges = []
            for i, (edges, edge_dict_key) in enumerate(zip(temp_edge_list, temp_edge_arity_dict)):
                if len(edges[0]) == 2:
                    binary_global_edges.extend(edges)
                if len(edges[0]) == 3:
                    ternary_global_edges.extend(edges)
            temp_edge_list.append(binary_global_edges)
            temp_edge_arity_dict["binaryEdge"] = len(binary_global_edges[0])
            if len(ternary_global_edges) != 0:
                temp_edge_list.append(ternary_global_edges)
                temp_edge_arity_dict["ternaryHyperEdge"] = len(ternary_global_edges[0])

        data["edge_list"]=temp_edge_list
        data["edge_arity_dict"]=temp_edge_arity_dict


        # if self._add_self_loop == True:
        #     slef_loop_edges = [[i, i] for i in range(len(data["x"]))]
        #     data["edge_list"].append(slef_loop_edges)
        #     data["edge_arity_dict"]["selfLoopEdges"] = len(slef_loop_edges[0])
        # if self._add_backward_edges == True:
        #     # todo could add backward edge as new edge type
        #     for i, (edges, edge_dict_key) in enumerate(zip(data["edge_list"], data["edge_arity_dict"])):
        #         if len(edges[0]) == 2 and edge_dict_key != "selfLoopEdges":
        #             backward_edges = [[edge[1], edge[0]] for edge in edges]
        #             data["edge_list"][i] = edges + backward_edges
        # if self._add_global_edges == True:
        #     binary_global_edges = []
        #     ternary_global_edges = []
        #     for i, (edges, edge_dict_key) in enumerate(zip(data["edge_list"], data["edge_arity_dict"])):
        #         if len(edges[0]) == 2:
        #             binary_global_edges.extend(edges)
        #         if len(edges[0]) == 3:
        #             ternary_global_edges.extend(edges)
        #     data["edge_list"].append(binary_global_edges)
        #     data["edge_arity_dict"]["binaryEdge"] = len(binary_global_edges[0])
        #     if len(ternary_global_edges) != 0:
        #         data["edge_list"].append(ternary_global_edges)
        #         data["edge_arity_dict"]["ternaryHyperEdge"] = len(ternary_global_edges[0])

        data["edge_list"] = [torch.tensor(edges, dtype=torch.long).t().contiguous() for edges in data["edge_list"]]

    def _construct_learning_label_and_edges(self, json_file_name, graph_edge_list, node_indices):
        if self.learning_task in ["template_binary_classification", "template_multi_classification"]:
            target_indices = read_one_filed(json_file_name, "labelIndices")
            target_label = read_one_filed(json_file_name, "labelList")
            graph_edge_list = graph_edge_list + ["templateEdge"]
            graph_edge_list = graph_edge_list + ["templateASTEdge"]
        elif self.learning_task == "argument_binary_classification":
            target_indices = node_indices
            argument_indices = read_one_filed(json_file_name, "argumentIndices")
            target_label = [1 if i in argument_indices else 0 for i in node_indices]
        elif self.learning_task in ["unsat_core_binary_classification"]:
            target_indices = read_one_filed(json_file_name, "labelIndices")
            target_label = read_one_filed(json_file_name, "labelList")
        else:
            target_indices = node_indices
            target_label = [1] * len(node_indices)
        return target_indices, target_label, graph_edge_list

    def _construct_edge_list(self, json_file_name, edge_list_fields, num_node):
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

        return edge_list, edge_arity_dict

    def tokenize_symbols(self, token_map, node_symbols, graph_type):
        canonical_symbol_key = ["relationSymbol", "relationSymbolArgument", "variable", "operator", "constant", "guard",
                                "clause", "clauseHead", "clauseBody", "clauseArgument", "templateBool", "templateEq",
                                "templateIneq"]
        unknown_node_map = {x: "unknown_" + x for x in canonical_symbol_key}

        converted_node_symbols = [convert_constant_to_category(word) for word in node_symbols]
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
                    tokenized_node_label_ids.append(token_map["unknown_0"])

        return tokenized_node_label_ids
