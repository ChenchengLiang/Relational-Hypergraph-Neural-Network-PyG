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
        '/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-backup.xlsx')
    linear_data = pd.read_excel(xls, 'linear')
    non_linear_data = pd.read_excel(xls, 'non-linear')
    print(linear_data.keys())

    linear_category_summary = get_category_summary(linear_data)
    non_linear_category_summary = get_category_summary(non_linear_data)


    linear_summary = get_statistic_summary(linear_data)
    non_linear_summary = get_statistic_summary(non_linear_data)

    # write to excel

    with pd.ExcelWriter(
            "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-summary.xlsx") as writer:
        linear_data.pop("Unnamed: 0")
        pd.DataFrame(pd.DataFrame(linear_data)).to_excel(writer, sheet_name="linear")
        non_linear_data.pop("Unnamed: 0")
        pd.DataFrame(pd.DataFrame(non_linear_data)).to_excel(writer, sheet_name="non_linear")
        pd.DataFrame(pd.DataFrame(linear_summary)).to_excel(writer, sheet_name="linear_summary")
        pd.DataFrame(pd.DataFrame(non_linear_summary)).to_excel(writer, sheet_name="non_linear_summary")
        pd.DataFrame(pd.DataFrame(linear_category_summary)).to_excel(writer, sheet_name="linear_category_summary")
        pd.DataFrame(pd.DataFrame(non_linear_category_summary)).to_excel(writer, sheet_name="non_linear_category_summary")


def get_category_summary(data_dict):
    category_dict={"category_name": [], "total_number":[],"safe_number": [], "unsafe_number": [], "unknown_number": []}
    category_list=sorted(list(set(data_dict["category"])))
    for c in category_list:
        satisfiability_in_one_category=get_target_row_by_condition(data_dict, "category", c, "satisfiability")
        category_dict["category_name"].append(c)
        category_dict["safe_number"].append(satisfiability_in_one_category.count("safe"))
        category_dict["unsafe_number"].append(satisfiability_in_one_category.count("unsafe"))
        category_dict["unknown_number"].append(satisfiability_in_one_category.count("unknown"))
        category_dict["total_number"].append(len(satisfiability_in_one_category))
    #add verification sum at last row
    category_dict["category_name"].append("verification_sum")
    category_dict["safe_number"].append(sum(category_dict["safe_number"]))
    category_dict["unsafe_number"].append(sum(category_dict["unsafe_number"]))
    category_dict["unknown_number"].append(sum(category_dict["unknown_number"]))
    category_dict["total_number"].append(sum(category_dict["total_number"]))

    return category_dict

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
