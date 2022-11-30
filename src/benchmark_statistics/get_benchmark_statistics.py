import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, select_key_with_value_condition, assign_dict_key_empty_list
import pandas as pd
from src.collect_results.utils import read_files, read_json_file, read_smt2_category
from src.collect_results.utils import get_min_max_solving_time


def main():
    #linear_total_file_list = get_linear_file_list()
    linear_total_file_list = get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test", "smt2")

    #non_linear_total_file_list = get_non_linear_file_list()
    non_linear_total_file_list = get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test-1", "smt2")

    data_dict = {"linear": {}, "non-linear": {}}

    # get file names
    data_dict["linear"]["file_name"] = [os.path.basename(x["file_name"]) for x in
                                        read_files(linear_total_file_list, file_type="",
                                                   read_function=read_smt2_category)]
    data_dict["non-linear"]["file_name"] = [os.path.basename(x["file_name"]) for x in
                                            read_files(non_linear_total_file_list, file_type="",
                                                       read_function=read_smt2_category)]
    # get fix smt attributes
    smt_measurements = ["file_size", "file_size_h", "category"]
    for sm in smt_measurements:
        data_dict["linear"][sm] = [x[sm] for x in
                                   read_files(linear_total_file_list, file_type="", read_function=read_smt2_category)]
        data_dict["non-linear"][sm] = [x[sm] for x in
                                       read_files(non_linear_total_file_list, file_type="",
                                                  read_function=read_smt2_category)]
    # get fix clause attributes
    fixed_clause_measurements = ["clauseNumberBeforeSimplification", "clauseNumberAfterSimplification",
                                 "relationSymbolNumberBeforeSimplification", "relationSymbolNumberAfterSimplification",
                                 # "minedSingleVariableTemplatesNumber", "minedBinaryVariableTemplatesNumber",
                                 # "minedTemplateNumber", "minedTemplateRelationSymbolNumber",
                                 # "labeledSingleVariableTemplatesNumber", "labeledBinaryVariableTemplatesNumber",
                                 # "labeledTemplateNumber", "labeledTemplateRelationSymbolNumber",
                                 # "unlabeledSingleVariableTemplatesNumber", "unlabeledBinaryVariableTemplatesNumber",
                                 # "unlabeledTemplateNumber", "unlabeledTemplateRelationSymbolNumber"
                                 ]
    for cm in fixed_clause_measurements:
        data_dict["linear"][cm] = list(get_fixed_filed_from_json_file(linear_total_file_list, cm))
        data_dict["non-linear"][cm] = list(get_fixed_filed_from_json_file(non_linear_total_file_list, cm))

    # get non-fix fields
    read_solving_time_from_json_file(linear_total_file_list, data_dict["linear"])
    read_solving_time_from_json_file(non_linear_total_file_list, data_dict["non-linear"])

    # get graph info
    read_graph_info_from_json_file(linear_total_file_list, data_dict["linear"])
    read_graph_info_from_json_file(non_linear_total_file_list, data_dict["non-linear"])

    # write to excel
    benchmark_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks"
    with pd.ExcelWriter(benchmark_folder + "/benchmark_statistics_split_clauses_1.xlsx") as writer:
        data = pd.DataFrame(pd.DataFrame(data_dict["linear"]))
        data.to_excel(writer, sheet_name="linear")
        data = pd.DataFrame(pd.DataFrame(data_dict["non-linear"]))
        data.to_excel(writer, sheet_name="non-linear")


def read_graph_info_from_json_file(file_list, statistic_dict):
    graph_fileds = ["CDHG_node_number", "CDHG_binary_edge_number", "CDHG_ternary_edge_number", "CDHG_label_number",
                    "CG_node_number", "CG_binary_edge_number", "CG_ternary_edge_number", "CG_label_number"]
    assign_dict_key_empty_list(statistic_dict, graph_fileds)
    for json_obj_CDHG, json_obj_CG in zip(
            read_files(file_list, file_type="hyperEdgeGraph.JSON", read_function=read_json_file),
            read_files(file_list, file_type="monoDirectionLayerGraph.JSON", read_function=read_json_file)):
        if len(json_obj_CDHG) >3 and len(json_obj_CG) > 3:
            statistic_dict["CDHG_node_number"].append(int(json_obj_CDHG["nodeNumber"][0]))
            statistic_dict["CDHG_binary_edge_number"].append(int(json_obj_CDHG["binaryEdgeNumber"][0]))
            statistic_dict["CDHG_ternary_edge_number"].append(int(json_obj_CDHG["ternaryHyperEdgeNumber"][0]))
            statistic_dict["CDHG_label_number"].append(int(json_obj_CDHG["labelNumber"][0]))
            statistic_dict["CG_node_number"].append(int(json_obj_CG["nodeNumber"][0]))
            statistic_dict["CG_binary_edge_number"].append(int(json_obj_CG["binaryEdgeNumber"][0]))
            statistic_dict["CG_ternary_edge_number"].append(int(json_obj_CG["ternaryHyperEdgeNumber"][0]))
            statistic_dict["CG_label_number"].append(int(json_obj_CG["labelNumber"][0]))
        else:
            statistic_dict["CDHG_node_number"].append(-1)
            statistic_dict["CDHG_binary_edge_number"].append(-1)
            statistic_dict["CDHG_ternary_edge_number"].append(-1)
            statistic_dict["CDHG_label_number"].append(-1)
            statistic_dict["CG_node_number"].append(-1)
            statistic_dict["CG_binary_edge_number"].append(-1)
            statistic_dict["CG_ternary_edge_number"].append(-1)
            statistic_dict["CG_label_number"].append(-1)


def read_solving_time_from_json_file(file_list, statistic_dict):
    record_fields = ["satisfiability",
                     "min_solving_time_option", "min_solving_time (s)",
                     "min_solving_time_cegar_interation_number",
                     "min_solving_time_generated_predicate_number",
                     "min_solving_time_average_predicate_size", "min_solving_time_predicate_generator_time",
                     "max_solving_time_option", "max_solving_time (s)",
                     "max_solving_time_cegar_interation_number", "max_solving_time_generated_predicate_number",
                     "max_solving_time_average_predicate_size", "max_solving_time_predicate_generator_time",
                     "solvable_option_list"]
    assign_dict_key_empty_list(statistic_dict, record_fields)
    for json_obj in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        if len(json_obj) != 0:  # has solvability file
            solving_time_dict = {}
            solvable_option_dict = {}
            for k in json_obj:
                if "solvingTime" in k:
                    solving_time_dict[k] = int(json_obj[k][0])
                    if int(json_obj[k][0]) != 10800000:
                        solvable_option_dict[k] = int(json_obj[k][0])
            if len(solving_time_dict) != 0:  # solvable with solvability file
                get_min_max_solving_time(solving_time_dict,statistic_dict,json_obj,min)
                get_min_max_solving_time(solving_time_dict, statistic_dict, json_obj, max)

                #satisfiability = get_satisfiability(json_obj, min_solving_option)
                satisfiability = get_satisfiability(json_obj, statistic_dict["min_solving_time_option"])

                statistic_dict["satisfiability"].append(satisfiability)
                statistic_dict["solvable_option_list"].append(
                    str([x.replace("solvingTime_", "") for x in solvable_option_dict.keys()]))

            else:  # unsolvable with solvability file
                assign_values_to_unsolvable_problem(statistic_dict)
        else:  # no solvability file
            assign_values_to_unsolvable_problem(statistic_dict)


def assign_values_to_unsolvable_problem(statistic_dict):
    statistic_dict["min_solving_time_option"].append("unsolvable")
    statistic_dict["min_solving_time (s)"].append(10800)
    statistic_dict["min_solving_time_cegar_interation_number"].append(10800000)
    statistic_dict["min_solving_time_generated_predicate_number"].append(10800000)
    statistic_dict["min_solving_time_average_predicate_size"].append(10800000)
    statistic_dict["min_solving_time_predicate_generator_time"].append(10800000)

    statistic_dict["max_solving_time_option"].append("unsolvable")
    statistic_dict["max_solving_time (s)"].append(10800)
    statistic_dict["max_solving_time_cegar_interation_number"].append(10800000)
    statistic_dict["max_solving_time_generated_predicate_number"].append(10800000)
    statistic_dict["max_solving_time_average_predicate_size"].append(10800000)
    statistic_dict["max_solving_time_predicate_generator_time"].append(10800000)

    statistic_dict["satisfiability"].append("unknown")
    statistic_dict["solvable_option_list"].append("")


def get_satisfiability(json_obj, min_solving_option):
    try:
        satisfiability = int(json_obj[min_solving_option.replace("solvingTime", "satisfiability")][0])
    except:
        satisfiability = int(json_obj["satisfiability"][0])

    if satisfiability == 1:
        return "safe"
    elif satisfiability == 0:
        return "unsafe"
    else:
        return "unknown"


def get_fixed_filed_from_json_file(file_list, field):
    for x in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        try:
            yield x[field][0]
        except:
            yield 10800000


def get_non_linear_file_list():
    sat_list_mining_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/2-uppmax-non-linear-mined-template/cluster_timeout_folder",
        "smt2")
    sat_list_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-non-linear-graphs/1-no_simplified_clauses",
        "smt2")
    sat_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-non-linear-graphs/cluster_timeout_folder",
        "smt2")
    sat_list_no_templates = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-non-linear-graphs/2-no_template",
        "smt2")
    sat_list_graph_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-non-linear-graphs/3-has-positive-labels",
        "smt2")
    sat_list_graph_no_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-non-linear-graphs/3-no-positive-labels",
        "smt2")
    sat_list = sat_list_mining_timeout + sat_list_no_simplified_clauses + sat_list_graph_timeout + sat_list_no_templates + sat_list_graph_postive_labels + sat_list_graph_no_postive_labels
    print("non-linear_sat_list", len(sat_list))

    unsolvable_list_labeling_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/4-uppmax-non-linear-unsolvable-unlabeled-tempaltes/cluster_timeout_folder",
        "smt2")
    unsolvable_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/5-uppmax-non-linear-unsolvable-graphs/cluster_timeout_folder",
        "smt2")
    unsolvable_list_graph = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/5-uppmax-non-linear-unsolvable-graphs/4-ready-for-training",
        "smt2")
    unsolvable_list = unsolvable_list_labeling_timeout + unsolvable_list_graph_timeout + unsolvable_list_graph
    print("non-linear_unsolvable_list", len(unsolvable_list))

    unsat_list = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/UNSAT-3668/solvability",
        "smt2")
    print("non-linear_unsat_list", len(unsat_list))
    # todo: get graphs

    no_simplified_clauses_list = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/no-simplified-clauses-1697/solvability",
        "smt2")
    print("non-linear_no_simplified_clauses_list", len(no_simplified_clauses_list))

    total_file_list = sat_list + unsolvable_list + unsat_list + no_simplified_clauses_list
    print("non-linear total_file_list", len(total_file_list))
    return total_file_list


def get_linear_file_list():
    # linear_sat_list_check_solvability_timeout=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/1-uppmax-linear-solvability/cluster_timeout_folder","smt2")
    linear_sat_list_check_mining_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/2-uppmax-linear-mined-template/cluster_timeout_folder",
        "smt2")
    linear_sat_list_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-linear-graphs/1-no_simplified_clauses",
        "smt2")
    linear_sat_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-linear-graphs/cluster_timeout_folder",
        "smt2")
    linear_sat_list_graph_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-linear-graphs/3-has-positive-labels",
        "smt2")
    linear_sat_list_graph_no_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-linear-graphs/3-no-positive-labels",
        "smt2")
    linear_sat_list = linear_sat_list_check_mining_timeout + linear_sat_list_no_simplified_clauses + linear_sat_list_graph_timeout + linear_sat_list_graph_postive_labels + linear_sat_list_graph_no_postive_labels
    print("linear_sat_list", len(linear_sat_list))



    linear_unsolvable_list_labeling_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/4-uppmax-linear-unsolvable-unlabeled-tempaltes/cluster_timeout_folder",
        "smt2")
    linear_unsolvable_list_labeling_unziped = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/4-uppmax-linear-unsolvable-unlabeled-tempaltes/unzip_files",
        "smt2")
    linear_unsolvable_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/5-uppmax-linear-unsolvable-graphs/cluster_timeout_folder",
        "smt2")
    linear_unsolvable_list_graph = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/5-uppmax-linear-unsolvable-graphs/4-ready-for-training",
        "smt2")
    linear_unsolvable_list_split_clause_solvable = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/unsolvable-1635/solvable-by-splitclauses0-19",
        "smt2")
    linear_unsolvable_list = linear_unsolvable_list_labeling_timeout + linear_unsolvable_list_labeling_unziped + linear_unsolvable_list_graph_timeout + linear_unsolvable_list_graph + linear_unsolvable_list_split_clause_solvable
    print("linear_unsolvable_list", len(linear_unsolvable_list))

    liner_unsat_list = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/UNSAT-2160/solvability",
        "smt2")
    print("liner_unsat_list",len(liner_unsat_list))
    # todo: get graphs

    linear_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/no-simplified-clauses-2068/solvability",
        "smt2")
    print("linear_no_simplified_clauses",len(linear_no_simplified_clauses))

    total_file_list = linear_sat_list + linear_unsolvable_list + liner_unsat_list + linear_no_simplified_clauses
    print("linear total_file_list", len(total_file_list))
    return total_file_list


if __name__ == '__main__':
    main()
