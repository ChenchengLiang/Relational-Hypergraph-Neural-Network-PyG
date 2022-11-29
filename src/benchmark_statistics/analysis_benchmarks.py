import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, select_key_with_value_condition, assign_dict_key_empty_list
import pandas as pd
from src.collect_results.utils import read_files, read_json_file, read_smt2_category


def main():
    #read excel
    xls = pd.ExcelFile('/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-backup (copy).xlsx')
    linear_data = pd.read_excel(xls, 'linear')
    non_linear_data = pd.read_excel(xls, 'non-linear')
    print(linear_data.keys())
    print(linear_data["file_name"].values)

    linear_category_set=set(linear_data["category"])
    non_linear_category_set = set(non_linear_data["category"])
    print("linear_category_set",len(linear_category_set))
    print("non_linear_category_set", len(non_linear_category_set))

    linear_safe={"category":[]}


    linear_summary=get_statistic_summary(linear_data)
    non_linear_summary = get_statistic_summary(non_linear_data)



    # write to excel

    with pd.ExcelWriter("/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-summary.xlsx") as writer:
        linear_data.pop("Unnamed: 0")
        data = pd.DataFrame(pd.DataFrame(linear_data))
        data.to_excel(writer, sheet_name="linear")
        non_linear_data.pop("Unnamed: 0")
        data = pd.DataFrame(pd.DataFrame(non_linear_data))
        data.to_excel(writer, sheet_name="non_linear")
        data = pd.DataFrame(pd.DataFrame(linear_summary))
        data.to_excel(writer, sheet_name="linear_summary")
        data = pd.DataFrame(pd.DataFrame(non_linear_summary))
        data.to_excel(writer, sheet_name="non_linear_summary")


def get_statistic_summary(data_dict):
    summary = {"statistic_name": [], "statistic_value": []}
    summary_dict={}
    summary_dict["safe_number"]=sum([1 if x == "safe" else 0 for x in data_dict["satisfiability"].values])

    summary_dict["unsafe_number"] = sum([1 if x == "unsafe" else 0 for x in data_dict["satisfiability"].values])

    summary_dict["unknown_number"] = sum([1 if x == "unknown" else 0 for x in data_dict["satisfiability"].values])



    for k in summary_dict:
        summary["statistic_name"].append(k)
        summary["statistic_value"].append(summary_dict[k])

    return summary


if __name__ == '__main__':
    main()
