import os.path
from src.utils import get_file_list
from utils import read_files, get_sumary_folder, read_json_file, read_graph_generation_log
import pandas as pd
from statistics import mean


def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-graphs/3-ready_for_training"
    #folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-graphs/ready_for_training"
    summary_folder = get_sumary_folder(folder)
    file_list = get_file_list(folder, "smt2")
    graph_type = {"hyperEdgeGraph": "CDHG", "monoDirectionLayerGraph": "CG"}
    binary_edge_name_list = [x + "Edge" for x in ["guard", "relationSymbolArgument", "ASTLeft", "ASTRight",
                                                  "AST", "relationSymbolInstance", "argumentInstance", "clauseHead",
                                                  "clauseBody",
                                                  "clauseArgument", "data", "quantifier", "binary", "template",
                                                  "templateAST"]]
    ternary_edge_name_list = [x + "HyperEdge" for x in ["controlFlow", "dataFlow", "ternary"]]
    node_field_list = ["node", "label"] + [x + "Indices" for x in
                                           ["relationSymbol", "initial", "false", "relationSymbolArgument", "variable",
                                            "operator", "constant", "guard", "clause", "clauseHead", "clauseBody",
                                            "clauseArgument",
                                            "templateBool", "templateEq", "templateIneq", "dummy", "unknown", "empty"]]
    data_dict = {"CDHG": {x + "Number": [] for x in node_field_list + binary_edge_name_list + ternary_edge_name_list},
                 "CG": {x + "Number": [] for x in node_field_list + binary_edge_name_list + ternary_edge_name_list}}
    data_dict["CDHG"].update({"fileName": [], "costruct_graph_time_consumption": []})
    data_dict["CG"].update({"fileName": [], "costruct_graph_time_consumption": []})
    for g in graph_type:
        graph_dict_list = read_files(file_list, g + ".JSON", read_function=read_json_file)
        time_consumption_list = read_files(file_list, file_type="log", read_function=read_graph_generation_log)
        for graph_dict, time_consumption_dict in zip(graph_dict_list, time_consumption_list):
            file_name = os.path.basename(graph_dict["file_name"])
            data_dict[graph_type[g]]["fileName"].append(file_name)
            data_dict[graph_type[g]]["costruct_graph_time_consumption"].append(
                time_consumption_dict[graph_type[g] + "_time_consumption"])
            for field in node_field_list + binary_edge_name_list + ternary_edge_name_list:
                data_dict[graph_type[g]][field + "Number"].append(graph_dict[field + "Number"][0])

    # print(data_dict["CDHG"])
    # print(data_dict["CG"])

    summary_dict={}
    for measurement in [mean, max, min]:
        measurement_str=measurement.__name__
        measurement_dict={"graph_type":["CDHG","CG"]}
        measurement_dict.update({measurement_str+"_"+x+"_number":[] for x in node_field_list + binary_edge_name_list + ternary_edge_name_list})
        for field in node_field_list + binary_edge_name_list + ternary_edge_name_list:
            measurement_dict[measurement_str+"_"+field+"_number"].append(measurement(data_dict["CDHG"][field+"Number"]))
            measurement_dict[measurement_str+"_" + field + "_number"].append(measurement(data_dict["CG"][field + "Number"]))
        summary_dict.update({measurement_str:measurement_dict})

    with pd.ExcelWriter(summary_folder + "/graph_statistics.xlsx") as writer:
        data = pd.DataFrame(pd.DataFrame(data_dict["CDHG"]))
        data.to_excel(writer, sheet_name="CDHG")
        data = pd.DataFrame(pd.DataFrame(data_dict["CG"]))
        data.to_excel(writer, sheet_name="CG")
        for k in summary_dict:
            data = pd.DataFrame(pd.DataFrame(summary_dict[k]))
            data.to_excel(writer, sheet_name=k)



if __name__ == '__main__':
    main()
