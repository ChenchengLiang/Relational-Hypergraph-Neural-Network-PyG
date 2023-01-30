from src.utils import assign_dict_key_empty_list
from src.collect_results.utils import read_files, read_json_file
from src.collect_results.utils import get_min_max_solving_time
from statistics import mean
from src.utils import camel_to_snake, make_dirct, read_a_json_field
from src.plots import scatter_plot
import itertools


def get_scatters(summary_folder, data_dict):
    scatter_folder = make_dirct(summary_folder + "/scatters")
    # combinations_list=["clauseNumberBeforeSimplification","clauseNumberAfterSimplification"]
    # combinations_pairs=itertools.combinations(combinations_list,2)
    combinations_pairs = [["clauseNumberBeforeSimplification", "clauseNumberAfterSimplification"],
                          # ["clauseNumberAfterSimplification", "clauseNumberAfterPruning"],#todo draw scatter with best threshold
                          ["relationSymbolNumberBeforeSimplification", "relationSymbolNumberAfterSimplification"],
                          # ["clauseNumberBeforeSimplification", "relationSymbolNumberBeforeSimplification"],
                          # ["clauseNumberAfterSimplification", "relationSymbolNumberAfterSimplification"],
                          ["clauseNumberAfterSimplification", "min_solving_time_cegar_interation_number"],
                          ["clauseNumberAfterSimplification", "min_solving_time (s)"],
                          ["CDHG_node_number", "min_solving_time (s)"],
                          ["CG_node_number", "min_solving_time (s)"],
                          ["clauseNumberAfterSimplification", "CDHG_node_number"],
                          ["clauseNumberAfterSimplification", "CDHG_label_number"],
                          ["clauseNumberAfterSimplification", "CG_node_number"],
                          ["clauseNumberAfterSimplification", "CG_label_number"],
                          ["CDHG_node_number", "CG_node_number"],
                          ]
    # z_data = data_dict["min_solving_time (s)"] if min(data_dict["min_solving_time (s)"]) != 10800 else []
    if data_dict["satisfiability-CDHG"] != "unknown":
        z_data = data_dict["satisfiability-CDHG"]
    elif data_dict["satisfiability-CG"] != "unknown":
        z_data = data_dict["satisfiability-CG"]
    elif data_dict["satisfiability"] != "unknown":
        z_data = data_dict["satisfiability"]
    else:
        z_data = "unknown"

    data_text = []
    for f, t1, t2 in zip(data_dict["file_name"], data_dict["threshold_list_CDHG"],
                         data_dict["threshold_list_CG"]):
        data_text.append(f + "\n" + "threshold_list_CDHG:" + str(t1) + "\n" + "threshold_list_CG:" + str(t2))
    for pairs in combinations_pairs:
        x_key = pairs[0]
        y_key = pairs[1]
        try:
            scatter_plot(x_data=data_dict[x_key], y_data=data_dict[y_key], z_data=z_data,
                         x_axis=x_key, y_axis=y_key, folder=scatter_folder, data_text=data_text,
                         name=x_key + "-" + y_key)
        except:
            print("no field", pairs)


def filter_rows(data_dict, column):
    index_list = []
    for i, v in enumerate(data_dict[column]):
        if v == 0 or v == 10800 or v == 10800000:
            index_list.append(i)

    temp_data_dict = {}
    assign_dict_key_empty_list(temp_data_dict, data_dict.keys())

    for k in data_dict:
        for i, v in enumerate(data_dict[k]):
            if i not in index_list:
                temp_data_dict[k].append(data_dict[k][i])
    return temp_data_dict


def filter_columns(data_dict):
    meaningless_keys = []
    for k in data_dict:
        if isinstance(data_dict[k][0], list):
            pass
        else:
            if len(set(data_dict[k])) == 1:
                meaningless_keys.append(k)
    for k in meaningless_keys:
        data_dict.pop(k)


def read_satisfiability(json_obj, min_solving_option):
    try:
        satisfiability = int(json_obj[min_solving_option.replace("solvingTime", "satisfiability")][0])
    except:
        try:
            satisfiability = int(json_obj["satisfiability"][0])
        except:
            satisfiability = -1
    return satisfiability


def read_graph_info_from_json_file(file_list, statistic_dict):
    graph_fileds = ["CDHG_node_number", "CDHG_binary_edge_number", "CDHG_ternary_edge_number", "CDHG_label_number",
                    "CG_node_number", "CG_binary_edge_number", "CG_ternary_edge_number", "CG_label_number"]
    assign_dict_key_empty_list(statistic_dict, graph_fileds)
    for json_obj_CDHG, json_obj_CG in zip(
            read_files(file_list, file_type="hyperEdgeGraph.JSON", read_function=read_json_file),
            read_files(file_list, file_type="monoDirectionLayerGraph.JSON", read_function=read_json_file)):
        if len(json_obj_CDHG) > 1 and len(json_obj_CG) > 1:
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
    record_fields = [
        "satisfiability",
        "no-pruning-satisfiability",
        "no-pruning-solving-time (s)",
        "improved_solving_time (s)",
        "satisfiability-CDHG",
        "clause_number_after_pruning_list_CDHG",
        "solving_time_list_CDHG (s)",
        "threshold_list_CDHG",
        "satisfiability-CG",
        "clause_number_after_pruning_list_CG",
        "solving_time_list_CG (s)",
        "threshold_list_CG",
        # "improved_solving_time_solvability",
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
        if len(json_obj) > 1:  # has solvability file
            solving_time_dict = {}
            solvable_option_dict = {}
            for k in json_obj:
                if "solvingTime_" in k:
                    solving_time_dict[k] = int(float(json_obj[k][0]))
                    if int(float(json_obj[k][0])) != 10800000:
                        solvable_option_dict[k] = int(float(json_obj[k][0]))
            if len(solving_time_dict) != 0:  # solvable with solvability file
                min_solving_option, min_solving_time = get_min_max_solving_time(solving_time_dict, statistic_dict,
                                                                                json_obj, min)
                max_solving_option, max_solving_time = get_min_max_solving_time(solving_time_dict, statistic_dict,
                                                                                json_obj, max)

                satisfiability = get_satisfiability(json_obj, min_solving_option)
                statistic_dict["satisfiability"].append(satisfiability)

                statistic_dict["solvable_option_list"].append(
                    str([x.replace("solvingTime_", "") for x in solvable_option_dict.keys()]))

                # record unsatcore reulsts
                threshold_list = get_unsatcore_threshold_list(json_obj)
                satisfiability_CDHG, clause_number_after_pruning_list_CDHG, threshold_list_CDHG, solving_time_list_CDHG, non_pruning_satisfiability_CDHG, non_pruning_solving_time_CDHG = get_fields_by_unsatcore_threshold(
                    json_obj, "CDHG", threshold_list=threshold_list)
                satisfiability_CG, clause_number_after_pruning_list_CG, threshold_list_CG, solving_time_list_CG, non_pruning_satisfiability_CG, non_pruning_solving_time_CG = get_fields_by_unsatcore_threshold(
                    json_obj, "CG", threshold_list=threshold_list)

                not_pruned_solving_time = min([non_pruning_solving_time_CDHG, non_pruning_solving_time_CG])
                statistic_dict["no-pruning-solving-time (s)"].append(non_pruning_satisfiability_CDHG)
                statistic_dict["no-pruning-satisfiability"].append(non_pruning_satisfiability_CDHG)
                statistic_dict["satisfiability-CDHG"].append(satisfiability_CDHG)
                statistic_dict["satisfiability-CG"].append(satisfiability_CG)
                statistic_dict["clause_number_after_pruning_list_CDHG"].append(clause_number_after_pruning_list_CDHG)
                statistic_dict["clause_number_after_pruning_list_CG"].append(clause_number_after_pruning_list_CG)
                statistic_dict["solving_time_list_CDHG (s)"].append(solving_time_list_CDHG)
                statistic_dict["solving_time_list_CG (s)"].append(solving_time_list_CG)
                statistic_dict["threshold_list_CDHG"].append(threshold_list_CDHG)
                statistic_dict["threshold_list_CG"].append(threshold_list_CG)

                # compute improved solving time using threshold 0 and other threshold
                pruned_unsatcore_min_solving_time = min(solving_time_list_CDHG + solving_time_list_CG)
                if pruned_unsatcore_min_solving_time != -0.001 and pruned_unsatcore_min_solving_time < not_pruned_solving_time:
                    improved_solving_time = not_pruned_solving_time - pruned_unsatcore_min_solving_time
                else:
                    improved_solving_time = 0
                statistic_dict["improved_solving_time (s)"].append(improved_solving_time)

                # compute improved solving time from previous solvability value
                # unsatcore_min_solving_time = min(solving_time_list_CDHG+solving_time_list_CG)
                # if unsatcore_min_solving_time!=-0.001 and unsatcore_min_solving_time < min_solving_time:
                #     improved_solving_time=min_solving_time - unsatcore_min_solving_time
                # else:
                #     improved_solving_time=0
                # statistic_dict["improved_solving_time_solvability"].append(improved_solving_time)




            else:  # unsolvable with solvability file
                assign_values_to_unsolvable_problem(statistic_dict, record_fields)

        else:  # no solvability file
            assign_values_to_unsolvable_problem(statistic_dict, record_fields)


def get_fields_by_unsatcore_threshold(json_obj, graph_type,
                                      threshold_list=[0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,
                                                      0.6]):
    measurement_list = ["satisfiability_list", "clause_number_after_pruning_list", "threshold_list",
                        "solving_time_list"]
    satisfiability_dict_key_list = []
    for x in ["safe", "unsafe", "unknown"]:
        for measure in measurement_list:
            satisfiability_dict_key_list.append(x + "_" + measure)

    satisfiability_dict = {}
    assign_dict_key_empty_list(satisfiability_dict, satisfiability_dict_key_list)
    non_pruning_satisfiability = -1
    non_pruning_solving_time = -1
    for t in threshold_list:
        suffix = "-" + graph_type + "-" + str(t)
        satisfiability = decode_satisfiability(float(read_a_json_field(json_obj, "satisfiability" + suffix)))
        clause_number_after_pruning = int(read_a_json_field(json_obj, "clauseNumberAfterPruning" + suffix))
        solving_time = int(float(read_a_json_field(json_obj, "solvingTime" + suffix))) / 1000
        if t == 0:
            non_pruning_satisfiability = satisfiability
            non_pruning_solving_time = solving_time

        if satisfiability == "safe":
            satisfiability_dict["safe_satisfiability_list"].append(satisfiability)
            satisfiability_dict["safe_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["safe_solving_time_list"].append(solving_time)
            satisfiability_dict["safe_threshold_list"].append(t)

        elif satisfiability == "unsafe":
            satisfiability_dict["unsafe_satisfiability_list"].append(satisfiability)
            satisfiability_dict["unsafe_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["unsafe_solving_time_list"].append(solving_time)
            satisfiability_dict["unsafe_threshold_list"].append(t)
        else:
            satisfiability_dict["unknown_satisfiability_list"].append(satisfiability)
            satisfiability_dict["unknown_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["unknown_solving_time_list"].append(solving_time)
            satisfiability_dict["unknown_threshold_list"].append(t)

    if len(satisfiability_dict["unsafe_satisfiability_list"]) != 0:
        return "unsafe", satisfiability_dict["unsafe_clause_number_after_pruning_list"], satisfiability_dict[
            "unsafe_threshold_list"], satisfiability_dict[
            "unsafe_solving_time_list"], non_pruning_satisfiability, non_pruning_solving_time
    elif len(satisfiability_dict["safe_satisfiability_list"]) != 0:
        return "safe", satisfiability_dict["safe_clause_number_after_pruning_list"], satisfiability_dict[
            "safe_threshold_list"], satisfiability_dict[
            "safe_solving_time_list"], non_pruning_satisfiability, non_pruning_solving_time
    else:
        return "unknown", satisfiability_dict["unknown_clause_number_after_pruning_list"], satisfiability_dict[
            "unknown_threshold_list"], satisfiability_dict[
            "unknown_solving_time_list"], non_pruning_satisfiability, non_pruning_solving_time


def get_unsatcore_threshold_list(json_obj):
    total_threshold_list = [round(0.01 * i, 2) for i in range(0, 100)]
    threshold_list = []
    for t in total_threshold_list:
        try:
            x = json_obj["clauseNumberAfterPruning-CG-" + str(t)]
            threshold_list.append(t)
        except:
            pass
    return threshold_list


def assign_values_to_unsolvable_problem(statistic_dict, record_fields):
    for rf in record_fields:
        if rf != "satisfiability":
            statistic_dict[rf].append(10800000)
        else:
            statistic_dict[rf].append("unknown")


def get_satisfiability(json_obj, min_solving_option):
    satisfiability = read_satisfiability(json_obj, min_solving_option)

    return decode_satisfiability(satisfiability)


def decode_satisfiability(satisfiability):
    if int(satisfiability) == 1:
        return "safe"
    elif int(satisfiability) == 0:
        return "unsafe"
    else:
        return "unknown"


def get_fixed_filed_from_json_file(file_list, field):
    for x in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        try:
            yield int(float(x[field][0]))
        except:
            yield 10800000


def get_category_summary(data_dict):
    basic_info_columns = ["category_name", "total_number", "safe_number", "unsafe_number", "unknown_number"]
    # could add any number fields corresponding to category column
    target_column_list = ["clauseNumberBeforeSimplification", "clauseNumberAfterSimplification", "min_solving_time (s)"]
    category_summary_columns = []
    for t in target_column_list:
        for x in ["min", "max", "mean", "sorted_mid"]:
            category_summary_columns.append(x + "_" + camel_to_snake(t))
    columns = basic_info_columns + category_summary_columns

    category_dict = {}
    assign_dict_key_empty_list(category_dict, columns)

    category_list = sorted(list(set(data_dict["category"])))
    for c in category_list:
        satisfiability_in_one_category = get_target_row_by_condition(data_dict, "category", c, "satisfiability")
        category_dict["category_name"].append(c)
        category_dict["safe_number"].append(satisfiability_in_one_category.count("safe"))
        category_dict["unsafe_number"].append(satisfiability_in_one_category.count("unsafe"))
        category_dict["unknown_number"].append(satisfiability_in_one_category.count("unknown"))
        category_dict["total_number"].append(len(satisfiability_in_one_category))

        min_max_mean_one_column_by_row(data_dict, category_dict, "category", c, "clauseNumberBeforeSimplification")
        min_max_mean_one_column_by_row(data_dict, category_dict, "category", c, "clauseNumberAfterSimplification")
        min_max_mean_one_column_by_row(data_dict, category_dict, "category", c, "min_solving_time (s)")

    # add verification sum at last row
    # category_dict["category_name"].append("verification_sum")
    # category_dict["safe_number"].append(sum(category_dict["safe_number"]))
    # category_dict["unsafe_number"].append(sum(category_dict["unsafe_number"]))
    # category_dict["unknown_number"].append(sum(category_dict["unknown_number"]))
    # category_dict["total_number"].append(sum(category_dict["total_number"]))
    # for x in category_summary_columns:
    #     category_dict[x].append(-1)

    return category_dict


def min_max_mean_one_column_by_row(data_dict, target_dict, column, one_row, terget_column):
    terget_column_in_one_category = get_target_row_by_condition(data_dict, column, one_row,
                                                                terget_column)
    terget_column_in_one_category = [float(x) for x in
                                     terget_column_in_one_category]
    for func in [min, max, mean, sorted_mid]:
        target_dict[func.__name__ + "_" + camel_to_snake(terget_column)].append(
            func(terget_column_in_one_category))


def sorted_mid(l):
    return sorted(l)[int(len(l) / 2)]


def get_statistic_summary(data_dict):
    summary = {"statistic_name": [], "statistic_value": []}
    summary_dict = {}
    satisfiability_list = get_dict_value(data_dict["satisfiability"])
    summary_dict["safe_number"] = sum([1 if x == "safe" else 0 for x in satisfiability_list])
    summary_dict["unsafe_number"] = sum([1 if x == "unsafe" else 0 for x in satisfiability_list])
    summary_dict["unknown_number"] = sum([1 if x == "unknown" else 0 for x in satisfiability_list])
    summary_dict["category_number"] = len(set(get_dict_value(data_dict["category"])))

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
                                                                               target_coloumn), prefix=cond,
                                       suffix=target_coloumn)

    for k in summary_dict:
        summary["statistic_name"].append(k)
        summary["statistic_value"].append(summary_dict[k])

    return summary


def write_min_max_mean_to_dict(summary_dict, target_list, prefix, suffix):
    suffix = camel_to_snake(suffix)
    target_list = [0] if len(target_list) == 0 else target_list
    target_list = [float(x) for x in target_list]
    for func in [min, max, mean, sorted_mid]:
        summary_dict[prefix + "_" + func.__name__ + "_" + suffix] = func(target_list)


def get_target_row_by_condition(data_dict, condition_column, condition, target_column):
    index = []
    for i, x in enumerate(get_dict_value(data_dict[condition_column])):
        if x == condition:
            index.append(i)
    return [get_dict_value(data_dict[target_column])[i] for i in index]


def get_dict_value(d):
    try:
        return d.values
    except:
        return d
