import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, select_key_with_value_condition,assign_dict_key_empty_list
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
                                 # "minedSingleVariableTemplatesNumber", "minedBinaryVariableTemplatesNumber",
                                 # "minedTemplateNumber", "minedTemplateRelationSymbolNumber",
                                 # "labeledSingleVariableTemplatesNumber", "labeledBinaryVariableTemplatesNumber",
                                 # "labeledTemplateNumber", "labeledTemplateRelationSymbolNumber",
                                 # "unlabeledSingleVariableTemplatesNumber", "unlabeledBinaryVariableTemplatesNumber",
                                 # "unlabeledTemplateNumber", "unlabeledTemplateRelationSymbolNumber"
                                 ]
    for cm in fixed_clause_measurements:
        data_dict["linear"][cm] = list(get_fixed_filed_from_json_file(linear_total_file_list,cm))
        data_dict["non-linear"][cm] = list(get_fixed_filed_from_json_file(non_linear_total_file_list,cm))


    #get non-fix fields
    read_solving_time_from_json_file(linear_total_file_list,data_dict["linear"])
    read_solving_time_from_json_file(non_linear_total_file_list,data_dict["non-linear"])


    #write to excel
    linear_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks"
    with pd.ExcelWriter(linear_folder + "/benchmark_statistics.xlsx") as writer:
        data = pd.DataFrame(pd.DataFrame(data_dict["linear"]))
        data.to_excel(writer, sheet_name="linear")
        data = pd.DataFrame(pd.DataFrame(data_dict["non-linear"]))
        data.to_excel(writer, sheet_name="non-linear")

def read_solving_time_from_json_file(file_list,statistic_dict):
    record_fields=["min_solving_time_option","min_solving_time (s)","max_solving_time_option","max_solving_time (s)","satisfiability","solvable_option_list"]
    assign_dict_key_empty_list(statistic_dict,record_fields)
    for json_obj in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        if len(json_obj)!=0: #has solvability file
            solving_time_dict={}
            solvable_option_dict={}
            for k in json_obj:
                if "solvingTime" in k:
                    solving_time_dict[k]=int(json_obj[k][0])
                    if int(json_obj[k][0])!=10800000:
                        solvable_option_dict[k]=int(json_obj[k][0])
            if len(solving_time_dict)!=0: #solvable with solvability file

                min_solving_option,min_solving_time=select_key_with_value_condition(solving_time_dict,min)
                max_solving_option, max_solving_time = select_key_with_value_condition(solving_time_dict, max)
                satisfiability = get_satisfiability(json_obj,min_solving_option)
                
                statistic_dict["min_solving_time_option"].append(min_solving_option.replace("solvingTime_",""))
                statistic_dict["min_solving_time (s)"].append(min_solving_time/1000)
                statistic_dict["max_solving_time_option"].append(max_solving_option.replace("solvingTime_",""))
                statistic_dict["max_solving_time (s)"].append(max_solving_time/1000)
                statistic_dict["satisfiability"].append(satisfiability)
                statistic_dict["solvable_option_list"].append(str([x.replace("solvingTime_","")for x in solvable_option_dict.keys()]))

            else: #unsolvable with solvability file
                statistic_dict["min_solving_time_option"].append("unsolvable")
                statistic_dict["min_solving_time (s)"].append(10800)
                statistic_dict["max_solving_time_option"].append("unsolvable")
                statistic_dict["max_solving_time (s)"].append(10800)
                statistic_dict["satisfiability"].append("unknown")
                statistic_dict["solvable_option_list"].append("")
        else:#no solvability file
            statistic_dict["min_solving_time_option"].append("unsolvable")
            statistic_dict["min_solving_time (s)"].append(10800)
            statistic_dict["max_solving_time_option"].append("unsolvable")
            statistic_dict["max_solving_time (s)"].append(10800)
            statistic_dict["satisfiability"].append("unknown")
            statistic_dict["solvable_option_list"].append("")





def get_satisfiability(json_obj,min_solving_option):
    satisfiability=int(json_obj[min_solving_option.replace("solvingTime","satisfiability")][0])
    if satisfiability==1:
        return "safe"
    elif satisfiability==0:
        return "unsafe"
    else:
        return "unknown"

def get_fixed_filed_from_json_file(file_list,field):
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
