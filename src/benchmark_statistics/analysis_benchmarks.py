import os.path
import sys

sys.path.append("../..")
from src.utils import get_file_list, select_key_with_value_condition, assign_dict_key_empty_list
import pandas as pd
from src.collect_results.utils import read_files, read_json_file, read_smt2_category
from statistics import mean
from src.utils import camel_to_snake


def main():
    # read excel
    xls = pd.ExcelFile(
        '/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-backup (copy).xlsx')
    linear_data = pd.read_excel(xls, 'linear')
    non_linear_data = pd.read_excel(xls, 'non-linear')
    print(linear_data.keys())

    linear_safe = {"category": []}

    linear_summary = get_statistic_summary(linear_data)
    non_linear_summary = get_statistic_summary(non_linear_data)

    # write to excel

    with pd.ExcelWriter(
            "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-summary.xlsx") as writer:
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
    summary_dict = {}
    summary_dict["safe_number"] = sum([1 if x == "safe" else 0 for x in data_dict["satisfiability"].values])
    summary_dict["unsafe_number"] = sum([1 if x == "unsafe" else 0 for x in data_dict["satisfiability"].values])
    summary_dict["unknown_number"] = sum([1 if x == "unknown" else 0 for x in data_dict["satisfiability"].values])
    summary_dict["category_number"] = len(set(data_dict["category"].values))

    safe_category = get_target_row_by_condition(data_dict, "satisfiability", "safe", "category")
    summary_dict["safe_category_number"] = len(set(safe_category))
    unsafe_category = get_target_row_by_condition(data_dict, "satisfiability", "unsafe", "category")
    summary_dict["unsafe_category_number"] = len(set(unsafe_category))
    unknown_category = get_target_row_by_condition(data_dict, "satisfiability", "unknown", "category")
    summary_dict["unknown_category_number"] = len(set(unknown_category))

    for cond in ["safe", "unsafe", "unknown"]:
        for target_coloumn in ["clauseNumberBeforeSimplification", "clauseNumberAfterSimplification",
                               "min_solving_time (s)", "min_solving_time_cegar_interation_number",
                               "min_solving_time_generated_predicate_number", "min_solving_time_average_predicate_size",
                               "min_solving_time_predicate_generator_time"]:
            write_min_max_mean_to_dict(summary_dict,
                                       target_list=get_target_row_by_condition(data_dict, "satisfiability", cond,
                                                                               target_coloumn), prefix=cond, suffix=target_coloumn)

    for k in summary_dict:
        summary["statistic_name"].append(k)
        summary["statistic_value"].append(summary_dict[k])

    return summary


def write_min_max_mean_to_dict(summary_dict, target_list, prefix, suffix):
    suffix = camel_to_snake(suffix)
    summary_dict[prefix + "_min_" + suffix] = min(target_list)
    summary_dict[prefix + "_max_" + suffix] = max(target_list)
    summary_dict[prefix + "_mean_" + suffix] = mean(target_list)


def get_target_row_by_condition(data_dict, condition_column, condition, target_column):
    index = []
    for i, x in enumerate(data_dict[condition_column].values):
        if x == condition:
            index.append(i)
    return [data_dict[target_column].values[i] for i in index]


if __name__ == '__main__':
    main()