import sys

sys.path.append("../..")
from utils import *
from src.utils import get_file_list
from src.plots import scatter_plot
import os
import pandas as pd
from src.collect_results.utils import read_files, read_smt2_category, get_sumary_folder


def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-unsatcore-linear-unknown-predicted-1-divided-324/train_data"
    summary_folder = get_sumary_folder(folder)
    folder_basename = os.path.basename(folder)

    file_list = get_file_list(folder, "smt2")
    data_dict = {}

    # get file names
    data_dict["file_name"] = [os.path.basename(x["file_name"]) for x in
                              read_files(file_list, file_type="",
                                         read_function=read_smt2_category)]
    # get fix smt attributes
    smt_measurements = ["file_size", "file_size_h", "category"]
    for sm in smt_measurements:
        data_dict[sm] = [x[sm] for x in
                         read_files(file_list, file_type="", read_function=read_smt2_category)]

        # get fix clause attributes
    fixed_clause_measurements = ["relationSymbolNumberBeforeSimplification", "relationSymbolNumberAfterSimplification",
                                 "clauseNumberBeforeSimplification", "clauseNumberAfterSimplification",
                                 # "clauseNumberAfterPruning",
                                 # "minedSingleVariableTemplatesNumber", "minedBinaryVariableTemplatesNumber",
                                 # "minedTemplateNumber", "minedTemplateRelationSymbolNumber",
                                 # "labeledSingleVariableTemplatesNumber", "labeledBinaryVariableTemplatesNumber",
                                 # "labeledTemplateNumber", "labeledTemplateRelationSymbolNumber",
                                 # "unlabeledSingleVariableTemplatesNumber", "unlabeledBinaryVariableTemplatesNumber",
                                 # "unlabeledTemplateNumber", "unlabeledTemplateRelationSymbolNumber"
                                 ]
    for cm in fixed_clause_measurements:
        data_dict[cm] = list(get_fixed_filed_from_json_file(file_list, cm))

    # get non-fix fields
    read_solving_time_from_json_file(file_list, data_dict)

    # get graph info
    read_graph_info_from_json_file(file_list, data_dict)

    get_scatters(summary_folder=summary_folder, data_dict=data_dict)

    # get summaries

    category_summary = get_category_summary(data_dict)

    statistic_summary = get_statistic_summary(data_dict)

    clause_prioritize_summary = get_summary_by_fields(data_dict, ["file_name", "file_size_h", "category",
                                                                  "clauseNumberAfterSimplification", "satisfiability",
                                                                  "no-pruning-satisfiability",
                                                                  "no-pruning-solving-time (s)",
                                                                  "improved_solving_time_prioritize_clauses (s)",
                                                                  "satisfiability-prioritize-clauses-CDHG",
                                                                  "solving-time-prioritize-clauses-CDHG",
                                                                  "satisfiability-prioritize-clauses-CG",
                                                                  "solving-time-prioritize-clauses-CG","prioritize_clauses_min_solving_time (s)",
                                                                  "CDHG_node_number", "CG_node_number"])
    clause_pruning_summary = get_summary_by_fields(data_dict, ["file_name", "file_size_h", "category",
                                                               "clauseNumberAfterSimplification", "satisfiability",
                                                               "no-pruning-satisfiability",
                                                               "no-pruning-solving-time (s)",
                                                               "improved_solving_time_threshold (s)",
                                                               "satisfiability-threshold-CDHG",
                                                               "clause_number_after_pruning_list_CDHG",
                                                               "solving_time_list_CDHG (s)",
                                                               "threshold_list_CDHG",
                                                               "satisfiability-threshold-CG",
                                                               "clause_number_after_pruning_list_CG",
                                                               "solving_time_list_CG (s)","pruned_unsatcore_min_solving_time (s)",
                                                               "threshold_list_CG" ])

    # filter list that has the same value
    # filter_columns(data_dict)
    filter_columns(category_summary)
    statistic_summary = filter_rows(statistic_summary, "statistic_value")

    # write to excel
    with pd.ExcelWriter(summary_folder + "/" + folder_basename + "_statistics_split_clauses_1.xlsx") as writer:
        pd.DataFrame(pd.DataFrame(data_dict)).to_excel(writer, sheet_name=folder_basename)
        pd.DataFrame(pd.DataFrame(category_summary)).to_excel(writer, sheet_name="category_summary")
        pd.DataFrame(pd.DataFrame(statistic_summary)).to_excel(writer, sheet_name="statistic_summary")
        pd.DataFrame(pd.DataFrame(clause_prioritize_summary)).to_excel(writer, sheet_name="clause_prioritize_summary")
        pd.DataFrame(pd.DataFrame(clause_pruning_summary)).to_excel(writer, sheet_name="clause_pruning_summary")


if __name__ == '__main__':
    main()
