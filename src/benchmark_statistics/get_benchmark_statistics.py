import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, unzip_file, compress_file
import pandas as pd
from src.collect_results.utils import read_files, read_json_file, read_smt2_category


def main():


    linear_total_file_list = get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test", "smt2")
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
                                 "minedSingleVariableTemplatesNumber", "minedBinaryVariableTemplatesNumber",
                                 "minedTemplateNumber", "minedTemplateRelationSymbolNumber",
                                 "labeledSingleVariableTemplatesNumber", "labeledBinaryVariableTemplatesNumber",
                                 "labeledTemplateNumber", "labeledTemplateRelationSymbolNumber",
                                 "unlabeledSingleVariableTemplatesNumber", "unlabeledBinaryVariableTemplatesNumber",
                                 "unlabeledTemplateNumber", "unlabeledTemplateRelationSymbolNumber"]
    for cm in fixed_clause_measurements:
        data_dict["linear"][cm] = list(get_filed_from_json_file(linear_total_file_list,cm))
        data_dict["non-linear"][cm] = list(get_filed_from_json_file(non_linear_total_file_list,cm))


    #write to excel
    linear_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks"
    with pd.ExcelWriter(linear_folder + "/benchmark_statistics.xlsx") as writer:
        data = pd.DataFrame(pd.DataFrame(data_dict["linear"]))
        data.to_excel(writer, sheet_name="linear")
        data = pd.DataFrame(pd.DataFrame(data_dict["non-linear"]))
        data.to_excel(writer, sheet_name="non-linear")


def get_filed_from_json_file(file_list,field):
    for x in read_files(file_list, file_type="solvability.JSON",read_function=read_json_file):
        try:
            yield x[field][0]
        except:
            yield 10800000
def get_linear_file_list():
    linear_sat_list_1=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/2-uppmax-linear-mined-template/ready_for_graph_construction","smt2")
    linear_sat_list_2=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/2-uppmax-linear-mined-template/cluster_timeout_folder","smt2")
    linear_sat_list=linear_sat_list_1+linear_sat_list_2
    linear_unsolvable_list=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/unsolvable-1616/train_data","smt2")
    liner_unsat_list=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/UNSAT-2160/solvability","smt2")
    linear_no_simplified_clauses=get_file_list("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/no-simplified-clauses-2087/train_data","smt2")


    total_file_list=linear_sat_list+linear_unsolvable_list+liner_unsat_list+linear_no_simplified_clauses
    print("total_file_list", len(total_file_list))
    return total_file_list

if __name__ == '__main__':
    main()
