from src.utils import assign_dict_key_empty_list
from src.collect_results.utils import read_files, read_json_file
from src.collect_results.utils import get_min_max_solving_time
from statistics import mean
from src.utils import camel_to_snake,make_dirct
from src.plots import scatter_plot
import itertools

def get_scatters(summary_folder,data_dict):
    scatter_folder = make_dirct(summary_folder + "/scatters")
    # combinations_list=["clauseNumberBeforeSimplification","clauseNumberAfterSimplification"]
    # combinations_pairs=itertools.combinations(combinations_list,2)
    combinations_pairs=[["clauseNumberBeforeSimplification","clauseNumberAfterSimplification"],
                        ["relationSymbolNumberBeforeSimplification", "relationSymbolNumberAfterSimplification"],
                        #["clauseNumberBeforeSimplification", "relationSymbolNumberBeforeSimplification"],
                        #["clauseNumberAfterSimplification", "relationSymbolNumberAfterSimplification"],
                        ["clauseNumberAfterSimplification","min_solving_time_cegar_interation_number"],
                        ["clauseNumberAfterSimplification", "min_solving_time (s)"],
                        ["CDHG_node_number", "min_solving_time (s)"],
                        ["CG_node_number", "min_solving_time (s)"],
                        ["clauseNumberAfterSimplification","CDHG_node_number"],
                        ["clauseNumberAfterSimplification", "CDHG_label_number"],
                        ["clauseNumberAfterSimplification", "CG_node_number"],
                        ["clauseNumberAfterSimplification", "CG_label_number"],
                        ["CDHG_node_number", "CG_node_number"],
                        ]
    z_data= data_dict["min_solving_time (s)"] if min(data_dict["min_solving_time (s)"])!=10800 else []
    for pairs in combinations_pairs:
        x_key = pairs[0]
        y_key = pairs[1]
        try:
            scatter_plot(x_data=data_dict[x_key], y_data=data_dict[y_key],z_data=z_data,
                         x_axis=x_key, y_axis=y_key, folder=scatter_folder, name=x_key + "-" + y_key)
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
        if len(json_obj) > 1:  # has solvability file
            solving_time_dict = {}
            solvable_option_dict = {}
            for k in json_obj:
                if "solvingTime" in k:
                    solving_time_dict[k] = int(json_obj[k][0])
                    if int(json_obj[k][0]) != 10800000:
                        solvable_option_dict[k] = int(json_obj[k][0])
            if len(solving_time_dict) != 0:  # solvable with solvability file
                min_solving_option = get_min_max_solving_time(solving_time_dict, statistic_dict, json_obj, min)
                max_solving_option = get_min_max_solving_time(solving_time_dict, statistic_dict, json_obj, max)

                satisfiability = get_satisfiability(json_obj, min_solving_option)

                statistic_dict["satisfiability"].append(satisfiability)
                statistic_dict["solvable_option_list"].append(
                    str([x.replace("solvingTime_", "") for x in solvable_option_dict.keys()]))

            else:  # unsolvable with solvability file
                assign_values_to_unsolvable_problem(statistic_dict, record_fields)

        else:  # no solvability file
            assign_values_to_unsolvable_problem(statistic_dict, record_fields)


#
def assign_values_to_unsolvable_problem(statistic_dict, record_fields):
    for rf in record_fields:
        if rf != "satisfiability":
            statistic_dict[rf].append(10800000)
        else:
            statistic_dict[rf].append("unknown")


def get_satisfiability(json_obj, min_solving_option):
    satisfiability = read_satisfiability(json_obj, min_solving_option)

    if satisfiability == 1:
        return "safe"
    elif satisfiability == 0:
        return "unsafe"
    else:
        return "unknown"


def get_fixed_filed_from_json_file(file_list, field):
    for x in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        try:
            yield int(x[field][0])
        except:
            yield 10800000


def get_category_summary(data_dict):
    basic_info_columns = ["category_name", "total_number", "safe_number", "unsafe_number", "unknown_number"]
    # could add any number fields corresponding to category column
    target_column_list = ["clauseNumberBeforeSimplification", "clauseNumberAfterSimplification", "min_solving_time (s)"]
    category_summary_columns = []
    for t in target_column_list:
        for x in ["min", "max", "mean","sorted_mid"]:
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
    return sorted(l)[int(len(l)/2)]

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
    for func in [min,max,mean,sorted_mid]:
        summary_dict[prefix + "_"+func.__name__+"_" + suffix] = func(target_list)



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
