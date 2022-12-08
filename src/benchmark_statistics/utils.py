from src.utils import assign_dict_key_empty_list
from src.collect_results.utils import read_files, read_json_file
from src.collect_results.utils import get_min_max_solving_time

def read_satisfiability(json_obj,min_solving_option):
    try:
        satisfiability = int(json_obj[min_solving_option.replace("solvingTime", "satisfiability")][0])
    except:
        try:
            satisfiability = int(json_obj["satisfiability"][0])
        except:
            satisfiability=-1
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
        if len(json_obj) > 1 :  # has solvability file
            solving_time_dict = {}
            solvable_option_dict = {}
            for k in json_obj:
                if "solvingTime" in k:
                    solving_time_dict[k] = int(json_obj[k][0])
                    if int(json_obj[k][0]) != 10800000:
                        solvable_option_dict[k] = int(json_obj[k][0])
            if len(solving_time_dict) != 0:  # solvable with solvability file
                min_solving_option=get_min_max_solving_time(solving_time_dict,statistic_dict,json_obj,min)
                max_solving_option=get_min_max_solving_time(solving_time_dict, statistic_dict, json_obj, max)

                satisfiability = get_satisfiability(json_obj, min_solving_option)


                statistic_dict["satisfiability"].append(satisfiability)
                statistic_dict["solvable_option_list"].append(
                    str([x.replace("solvingTime_", "") for x in solvable_option_dict.keys()]))

            else:  # unsolvable with solvability file
                assign_values_to_unsolvable_problem(statistic_dict,record_fields)

        else:  # no solvability file
            assign_values_to_unsolvable_problem(statistic_dict,record_fields)


#
def assign_values_to_unsolvable_problem(statistic_dict,record_fields):
    for rf in record_fields:
        if rf != "satisfiability":
            statistic_dict[rf].append(10800000)
        else:
            statistic_dict[rf].append("unknown")




def get_satisfiability(json_obj, min_solving_option):
    satisfiability=read_satisfiability(json_obj, min_solving_option)

    if satisfiability == 1:
        return "safe"
    elif satisfiability == 0:
        return "unsafe"
    else:
        return "unknown"


def get_fixed_filed_from_json_file(file_list, field):
    for x in read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
        try:
            yield x[field][0]
        except:
            yield 10800000
