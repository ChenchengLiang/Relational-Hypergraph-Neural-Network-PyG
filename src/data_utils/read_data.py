import sys
sys.path.append("../../")
from os.path import join as opj

import mlflow

from src.data_utils.dataset import HornGraphDataset
from src.utils import remove_processed_file, unzip_file, read_one_filed, get_file_list, convert_constant_to_category
from src.plots import draw_label_pie_chart
from torch_geometric.loader import DataLoader
import os


def get_data(params):
    cdhg_edge_type=["relationSymbolArgumentEdge", "ASTLeftEdge", "ASTRightEdge", "ASTEdge", "guardEdge",
     "quantifierEdge",
     "controlFlowHyperEdge", "dataFlowHyperEdge"]
    cg_edge_type=["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
     "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge", "ASTLeftEdge",
     "ASTRightEdge", "ASTEdge", "guardEdge", "dataEdge",
     "quantifierEdge"
     ]
    if params["reload_data"]==True:
        params["edge_types"] =  cdhg_edge_type if params["graph_type"]=="hyperEdgeGraph" else cg_edge_type

    vocabulary, token_map = build_vocabulary(params)
    mlflow.log_dict(token_map, "token_map.json")

    root = opj(params["benchmark"], "train_data")
    if params["reload_data"] == True:
        remove_processed_file(root=root)
    train_data = HornGraphDataset(params=params, root=root, token_map=token_map)

    root = opj(params["benchmark"], "valid_data")
    if params["reload_data"] == True:
        remove_processed_file(root=root)
    valid_data = HornGraphDataset(params=params, root=root, token_map=token_map)

    root = opj(params["benchmark"], "test_data")
    if params["reload_data"] == True:
        remove_processed_file(root=root)
    test_data = HornGraphDataset(params=params, root=root, token_map=token_map)

    dataset = train_data + valid_data + test_data
    vocabulary_size = len(vocabulary)
    print("vocabulary_size", vocabulary_size)
    params["vocabulary_size"]=vocabulary_size

    # train_data = dataset
    # valid_data = train_data
    # test_data = train_data
    train_valid_test_number = [len(train_data), len(valid_data), len(test_data)]
    print("train-valid-test:", train_valid_test_number)
    print("train_data[0]", train_data[0])
    # print("train_data[0].y", train_data[0].y)

    train_loader = DataLoader(train_data, batch_size=params["batch_size"], shuffle=params["data_loader_shuffle"])
    valid_loader = DataLoader(valid_data, batch_size=params["batch_size"], shuffle=params["data_loader_shuffle"])
    test_loader = DataLoader(test_data, batch_size=params["batch_size"], shuffle=params["data_loader_shuffle"])

    edge_arity_dict = train_data[0].edge_arity_dict

    dataset_distribution_values = draw_label_pie_chart(params["num_classes"], lambda: (t.y for t in dataset),
                                                       params["benchmark"],
                                                       "all-data")

    draw_label_pie_chart(params["num_classes"], lambda: (t.y for t in train_data), params["benchmark"], "train-data")
    draw_label_pie_chart(params["num_classes"], lambda: (t.y for t in valid_data), params["benchmark"], "valid-data")
    draw_label_pie_chart(params["num_classes"], lambda: (t.y for t in test_data), params["benchmark"], "test-data")
    class_weight = [(1 - (v / sum(dataset_distribution_values))) * 10 for v in dataset_distribution_values] if params[
                                                                                                            "use_class_weight"] == True else [
        1 for v in dataset_distribution_values]
    print("class_weight", class_weight)
    params["class_weight"] = class_weight
    params["edge_arity_dict"] = edge_arity_dict
    params["train_valid_test"] = train_valid_test_number

    return edge_arity_dict, train_loader, valid_loader, test_loader, vocabulary_size, params


def build_fixed_vocabulary(params):
    fixed_symbol = ["initial_0", "false_0", "dummy_0", "unknown", "empty"]
    canonical_symbol_key = ["relationSymbol", "relationSymbolArgument", "variable", "operator", "constant", "guard",
                            "clause", "clauseHead", "clauseBody", "clauseArgument", "templateBool", "templateEq",
                            "templateIneq"]
    canonical_symbol = []
    for x in canonical_symbol_key:
        for i in range(0, 1000000):
            canonical_symbol.append(x + "_" + str(i))

    vocabulary_set = fixed_symbol + canonical_symbol

    token_map = {}
    token_id = 0

    vocabulary_set = set([convert_constant_to_category(w) for w in vocabulary_set])
    for word in sorted(vocabulary_set):
        token_map[word] = token_id
        token_id = token_id + 1
    # print("vocabulary_set",len(vocabulary_set),vocabulary_set)
    # print("token_map",len(token_map),token_map)
    return vocabulary_set, token_map


def build_vocabulary(params):
    total_file_list = []
    for fold in ["train_data", "valid_data", "test_data"]:
        folder = opj(params["benchmark"], fold) + "/raw"
        total_file_list += get_file_list(folder, "." + params["graph_type"] + ".JSON")

    fixed_symbol = ["initial_0", "false_0", "dummy_0", "unknown_0", "empty"]
    canonical_symbol_key = ["relationSymbol", "relationSymbolArgument", "variable", "operator", "constant", "guard",
                            "clause", "clauseHead", "clauseBody", "clauseArgument", "templateBool", "templateEq",
                            "templateIneq"]
    initial_vocabulary_set = set(
        ["unknown_" + t for t in canonical_symbol_key] + fixed_symbol)
    vocabulary_set = initial_vocabulary_set

    for file_name in total_file_list:
        unzip_file(file_name)
        json_file_name = file_name[:-len(".zip")]
        node_symbol_list = read_one_filed(json_file_name, "nodeSymbolList")
        vocabulary_set.update(node_symbol_list)
        if os.path.exists(json_file_name):
            os.remove(json_file_name)

    token_map = {}
    token_id = 0

    vocabulary_set = set([convert_constant_to_category(w) for w in vocabulary_set])
    for word in sorted(vocabulary_set):
        token_map[word] = token_id
        token_id = token_id + 1
    # print("vocabulary_set",len(vocabulary_set),vocabulary_set)
    # print("token_map",len(token_map),token_map)
    return vocabulary_set, token_map
