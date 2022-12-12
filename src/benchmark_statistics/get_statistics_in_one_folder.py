import sys

sys.path.append("../..")
from utils import *
from src.utils import get_file_list
import os
import pandas as pd
from src.collect_results.utils import read_files, read_smt2_category
def main():
    folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-non-Liner-dateset-new/tempalte-selection-data/train+unknown"
    folder_basename=os.path.basename(folder)

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
        data_dict[cm] = list(get_fixed_filed_from_json_file(file_list, cm))

    # get non-fix fields
    read_solving_time_from_json_file(file_list, data_dict)

    # get graph info
    read_graph_info_from_json_file(file_list, data_dict)

    category_summary = get_category_summary(data_dict)

    statistic_summary = get_statistic_summary(data_dict)

    #filter list that has the same value
    filter_columns(data_dict)
    filter_columns(category_summary)
    statistic_summary=filter_rows(statistic_summary, "statistic_value")


    # write to excel
    benchmark_folder = os.path.dirname(folder)
    with pd.ExcelWriter(benchmark_folder + "/"+folder_basename+"_statistics_split_clauses_1.xlsx") as writer:
        pd.DataFrame(pd.DataFrame(data_dict)).to_excel(writer, sheet_name=folder_basename)
        pd.DataFrame(pd.DataFrame(category_summary)).to_excel(writer, sheet_name="category_summary")
        pd.DataFrame(pd.DataFrame(statistic_summary)).to_excel(writer, sheet_name="statistic_summary")


if __name__ == '__main__':
    main()