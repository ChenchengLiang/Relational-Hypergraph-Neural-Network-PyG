import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, select_key_with_value_condition, assign_dict_key_empty_list
import pandas as pd
from src.collect_results.utils import read_files, read_json_file, read_smt2_category
from utils import read_graph_info_from_json_file,get_fixed_filed_from_json_file,read_solving_time_from_json_file

def main():
    linear_total_file_list = get_linear_file_list()
    #linear_total_file_list = get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test", "smt2")

    non_linear_total_file_list = get_non_linear_file_list()
    #non_linear_total_file_list = get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test-1", "smt2")

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



def get_non_linear_file_list():
    sat_list_mining_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/2-uppmax-SAT-mined-template/cluster_timeout_folder",
        "smt2")
    sat_list_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/1-no_simplified_clauses",
        "smt2")
    sat_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/cluster_timeout_folder",
        "smt2")
    sat_list_no_templates = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/2-no_template",
        "smt2")
    sat_list_graph_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/3-has-positive-labels",
        "smt2")
    sat_list_graph_no_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/3-no-positive-labels",
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
    unsolvable_list_in_unsat = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/UNSAT-3668/cluster_timeout_folder",
        "smt2")
    unsolvable_list = unsolvable_list_labeling_timeout + unsolvable_list_graph_timeout + unsolvable_list_graph + unsolvable_list_in_unsat
    print("non-linear_unsolvable_list", len(unsolvable_list))

    unsat_list = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/splitClause1/UNSAT-3668/ready_for_counter_example_mining",
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
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/2-uppmax-SAT-mined-template/cluster_timeout_folder",
        "smt2")
    linear_sat_list_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/1-no_simplified_clauses",
        "smt2")
    linear_sat_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/cluster_timeout_folder",
        "smt2")
    linear_sat_list_graph_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/3-has-positive-labels",
        "smt2")
    linear_sat_list_graph_no_postive_labels = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-SAT-graphs/3-no-positive-labels",
        "smt2")
    linear_sat_list = linear_sat_list_check_mining_timeout + linear_sat_list_no_simplified_clauses + linear_sat_list_graph_timeout + linear_sat_list_graph_postive_labels + linear_sat_list_graph_no_postive_labels
    print("linear_sat_list", len(linear_sat_list))



    unsolvable_list_labeling_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/4-uppmax-linear-unsolvable-unlabeled-tempaltes/cluster_timeout_folder",
        "smt2")
    unsolvable_list_labeling_unziped = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/4-uppmax-linear-unsolvable-unlabeled-tempaltes/unzip_files",
        "smt2")
    unsolvable_list_graph_timeout = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/5-uppmax-linear-unsolvable-graphs/cluster_timeout_folder",
        "smt2")
    unsolvable_list_graph = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/5-uppmax-linear-unsolvable-graphs/4-ready-for-training",
        "smt2")
    unsolvable_list_split_clause_solvable = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/unsolvable-1635/solvable-by-splitclauses0-19",
        "smt2")
    unsolvable_list_in_unsat = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/UNSAT-2160/cluster_timeout_folder",
        "smt2")
    linear_unsolvable_list = unsolvable_list_labeling_timeout + unsolvable_list_labeling_unziped + \
                             unsolvable_list_graph_timeout + unsolvable_list_graph + unsolvable_list_split_clause_solvable \
                             + unsolvable_list_in_unsat
    print("linear_unsolvable_list", len(linear_unsolvable_list))

    linear_unsat_list = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/UNSAT-2160/ready_for_counter_example_mining",
        "smt2")
    print("liner_unsat_list",len(linear_unsat_list))
    # todo: get graphs

    linear_no_simplified_clauses = get_file_list(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/no-simplified-clauses-2068/solvability",
        "smt2")
    print("linear_no_simplified_clauses",len(linear_no_simplified_clauses))

    total_file_list = linear_sat_list + linear_unsolvable_list + linear_unsat_list + linear_no_simplified_clauses
    print("linear total_file_list", len(total_file_list))
    return total_file_list


if __name__ == '__main__':
    main()
