from src.utils import assign_dict_key_empty_list
from src.collect_results.utils import read_files, read_json_file
from src.collect_results.utils import get_min_max_solving_time
from statistics import mean, stdev
from src.utils import camel_to_snake, make_dirct, read_a_json_field, get_file_list
from src.plots import scatter_plot
import itertools
import pandas as pd
from src.collect_results.utils import read_files, read_smt2_category, get_sumary_folder
import os


def get_statistiics_in_one_folder(folder):
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
                                                                  "no-pruning-cegar_itartion",
                                                                  "improved_solving_time_prioritize_clauses (s)",
                                                                  "improved_cegar_iteration_prioritize_clauses",
                                                                  "satisfiability-prioritize-clauses-CDHG",
                                                                  "solving-time-prioritize-clauses-CDHG",
                                                                  "cegar_iteration-prioritize-clauses-CDHG",
                                                                  "satisfiability-prioritize-clauses-CG",
                                                                  "cegar_iteration-prioritize-clauses-CG",
                                                                  "solving-time-prioritize-clauses-CG",
                                                                  "prioritize_clauses_min_solving_time (s)",
                                                                  "prioritize_clauses_min_cegar_iteration",
                                                                  "CDHG_node_number", "CG_node_number"])
    clause_pruning_summary = get_summary_by_fields(data_dict, ["file_name", "file_size_h", "category",
                                                               "clauseNumberAfterSimplification", "satisfiability",
                                                               "no-pruning-satisfiability",
                                                               "no-pruning-solving-time (s)",
                                                               "no-pruning-cegar_itartion",
                                                               "improved_solving_time_threshold (s)",
                                                               "improved_cegar_iteartion_threshold",
                                                               "satisfiability-threshold-CDHG",
                                                               "clause_number_after_pruning_list_CDHG",
                                                               "solving_time_list_CDHG (s)",
                                                               "threshold_list_CDHG",
                                                               "satisfiability-threshold-CG",
                                                               "clause_number_after_pruning_list_CG",
                                                               "solving_time_list_CG (s)",
                                                               "pruned_unsatcore_min_solving_time (s)",
                                                               "pruned_unsatcore_min_cegar_iteration",
                                                               "threshold_list_CG"])

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
                          ["no-pruning-solving-time (s)", "solving-time-prioritize-clauses-CDHG"],
                          ["no-pruning-solving-time (s)", "solving-time-prioritize-clauses-CG"],
                          ["no-pruning-solving-time (s)", "prioritize_clauses_min_solving_time (s)"],
                          ["no-pruning-solving-time (s)", "pruned_unsatcore_min_solving_time (s)"],
                          ["no-pruning-cegar_itartion", "prioritize_clauses_min_cegar_iteration"],
                          ["no-pruning-cegar_itartion", "cegar_iteration-prioritize-clauses-CDHG"],
                          ["no-pruning-cegar_itartion", "cegar_iteration-prioritize-clauses-CG"],
                          ["no-pruning-cegar_itartion", "pruned_unsatcore_min_cegar_iteration"],
                          ]
    # z_data = data_dict["min_solving_time (s)"] if min(data_dict["min_solving_time (s)"]) != 10800 else []
    z_data = []
    for p_cdhg, p_cg, t_cdhg, t_cg, s in zip(data_dict["satisfiability-prioritize-clauses-CDHG"],
                                             data_dict["satisfiability-prioritize-clauses-CG"],
                                             data_dict["satisfiability-threshold-CDHG"],
                                             data_dict["satisfiability-threshold-CG"], data_dict["satisfiability"]):
        if p_cdhg != "unknown":
            z_data.append(p_cdhg)
        elif p_cg != "unknown":
            z_data.append(p_cg)
        elif t_cdhg != "unknown":
            z_data.append(t_cdhg)
        elif t_cg != "unknown":
            z_data.append(t_cdhg)
        elif s != "unknown":
            z_data.append(s)
        else:
            z_data.append("unknown")

    data_dict["satisfiability"] = z_data
    data_text = []
    for f, t1, t2 in zip(data_dict["file_name"], data_dict["threshold_list_CDHG"],
                         data_dict["threshold_list_CG"]):
        if len(t2) > 30:
            t2 = "unknown"
        if len(t1) > 30:
            t1 = "unknown"
        data_text.append(f + "\n" + "threshold_list_CDHG:" + str(t1) + "\n" + "threshold_list_CG:" + str(t2) + "\n")

    for pairs in combinations_pairs:
        x_key = pairs[0]
        y_key = pairs[1]
        try:
            scatter_plot(x_data=data_dict[x_key], y_data=data_dict[y_key], z_data=z_data,
                         x_axis=x_key, y_axis=y_key, folder=scatter_folder, data_text=data_text,
                         name=x_key + " vs. " + y_key)
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
            satisfiability = int(float(json_obj["satisfiability"][0]))
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
        "no-pruning-cegar_itartion",
        # prioritized
        "improved_solving_time_prioritize_clauses (s)",
        "improved_cegar_iteration_prioritize_clauses",
        "satisfiability-prioritize-clauses-CDHG",
        "solving-time-prioritize-clauses-CDHG",
        "cegar_iteration-prioritize-clauses-CDHG",
        "satisfiability-prioritize-clauses-CG",
        "solving-time-prioritize-clauses-CG",
        "cegar_iteration-prioritize-clauses-CG",
        "prioritize_clauses_min_solving_time (s)",
        "prioritize_clauses_min_cegar_iteration",
        # threshold
        "improved_solving_time_threshold (s)",
        "improved_cegar_iteartion_threshold",
        "satisfiability-threshold-CDHG",
        "clause_number_after_pruning_list_CDHG",
        "solving_time_list_CDHG (s)",
        "threshold_list_CDHG",
        "cegar_iteration_list_CDHG",
        "satisfiability-threshold-CG",
        "clause_number_after_pruning_list_CG",
        "solving_time_list_CG (s)",
        "threshold_list_CG",
        "cegar_iteration_list_CG",
        "pruned_unsatcore_min_solving_time (s)",
        "pruned_unsatcore_min_cegar_iteration",
        # templates
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

                # record unsatcore threhold reulsts
                threshold_list = get_unsatcore_threshold_list(json_obj)
                satisfiability_threshold_CDHG, clause_number_after_pruning_list_CDHG, threshold_list_CDHG, solving_time_list_CDHG, cegar_number_list_CDHG, \
                    non_pruning_satisfiability_CDHG, non_pruning_solving_time_CDHG, non_pruning_cegar_iteration_CDHG = get_fields_by_unsatcore_threshold(
                    json_obj, "CDHG", threshold_list=threshold_list)
                satisfiability_threshold_CG, clause_number_after_pruning_list_CG, threshold_list_CG, solving_time_list_CG, cegar_number_list_CG, \
                    non_pruning_satisfiability_CG, non_pruning_solving_time_CG, non_pruning_cegar_iteration_CG = get_fields_by_unsatcore_threshold(
                    json_obj, "CG", threshold_list=threshold_list)

                non_pruning_solving_time = get_min_number_from_list(
                    [non_pruning_solving_time_CDHG, non_pruning_solving_time_CG], -0.001)
                non_pruning_cegar_iteration = get_min_number_from_list(
                    [non_pruning_cegar_iteration_CDHG, non_pruning_cegar_iteration_CG], -1)

                statistic_dict["no-pruning-solving-time (s)"].append(non_pruning_solving_time)
                statistic_dict["no-pruning-satisfiability"].append(non_pruning_satisfiability_CDHG)
                statistic_dict["no-pruning-cegar_itartion"].append(non_pruning_cegar_iteration)
                statistic_dict["satisfiability-threshold-CDHG"].append(satisfiability_threshold_CDHG)
                statistic_dict["satisfiability-threshold-CG"].append(satisfiability_threshold_CG)
                statistic_dict["clause_number_after_pruning_list_CDHG"].append(clause_number_after_pruning_list_CDHG)
                statistic_dict["clause_number_after_pruning_list_CG"].append(clause_number_after_pruning_list_CG)
                statistic_dict["solving_time_list_CDHG (s)"].append(solving_time_list_CDHG)
                statistic_dict["solving_time_list_CG (s)"].append(solving_time_list_CG)
                statistic_dict["threshold_list_CDHG"].append(threshold_list_CDHG)
                statistic_dict["threshold_list_CG"].append(threshold_list_CG)
                statistic_dict["cegar_iteration_list_CDHG"].append(cegar_number_list_CDHG)
                statistic_dict["cegar_iteration_list_CG"].append(cegar_number_list_CG)

                # compute improved solving time using threshold 0 and other threshold
                pruned_unsatcore_min_solving_time = get_min_number_from_list(
                    solving_time_list_CDHG + solving_time_list_CG, -0.001)
                pruned_unsatcore_min_cegar_iteartion = get_min_number_from_list(
                    cegar_number_list_CDHG + cegar_number_list_CG, -1)

                improved_solving_time = get_improved_field(non_pruning_solving_time, pruned_unsatcore_min_solving_time,
                                                           -0.001)
                improved_cegar_iteration = get_improved_field(non_pruning_cegar_iteration,
                                                              pruned_unsatcore_min_cegar_iteartion, -1)

                statistic_dict["improved_solving_time_threshold (s)"].append(improved_solving_time)
                statistic_dict["improved_cegar_iteartion_threshold"].append(improved_cegar_iteration)
                statistic_dict["pruned_unsatcore_min_solving_time (s)"].append(pruned_unsatcore_min_solving_time)
                statistic_dict["pruned_unsatcore_min_cegar_iteration"].append(pruned_unsatcore_min_cegar_iteartion)

                # record unsatcore clause prioritize reulsts
                satisfiability_prioritize_clauses_CDHG, solving_time_prioritize_clauses_CDHG, cega_iteration_CDHG = get_fields_by_unsatcore_prioritize_clauses(
                    json_obj, "CDHG")
                satisfiability_prioritize_clauses_CG, solving_time_prioritize_clauses_CG, cega_iteration_CG = get_fields_by_unsatcore_prioritize_clauses(
                    json_obj, "CG")

                statistic_dict["satisfiability-prioritize-clauses-CDHG"].append(satisfiability_prioritize_clauses_CDHG)
                statistic_dict["satisfiability-prioritize-clauses-CG"].append(satisfiability_prioritize_clauses_CG)
                statistic_dict["solving-time-prioritize-clauses-CDHG"].append(solving_time_prioritize_clauses_CDHG)
                statistic_dict["solving-time-prioritize-clauses-CG"].append(solving_time_prioritize_clauses_CG)
                statistic_dict["cegar_iteration-prioritize-clauses-CDHG"].append(cega_iteration_CDHG)
                statistic_dict["cegar_iteration-prioritize-clauses-CG"].append(cega_iteration_CG)
                # compute improved solving time using threshold 0 and prioritize-clauses
                prioritize_clauses_min_solving_time = get_min_number_from_list(
                    [solving_time_prioritize_clauses_CDHG, solving_time_prioritize_clauses_CG], -0.001)
                prioritize_clauses_min_cegar_iteration = get_min_number_from_list(
                    [cega_iteration_CDHG, cega_iteration_CG], -1)

                prioritize_clauses_improved_solving_time = get_improved_field(non_pruning_solving_time,
                                                                              prioritize_clauses_min_solving_time,
                                                                              -0.001)
                prioritize_clauses_improved_cegar_iteration = get_improved_field(non_pruning_cegar_iteration,
                                                                                 prioritize_clauses_min_cegar_iteration,
                                                                                 -1)

                statistic_dict["improved_solving_time_prioritize_clauses (s)"].append(
                    prioritize_clauses_improved_solving_time)
                statistic_dict["improved_cegar_iteration_prioritize_clauses"].append(
                    prioritize_clauses_improved_cegar_iteration)
                statistic_dict["prioritize_clauses_min_solving_time (s)"].append(
                    prioritize_clauses_min_solving_time)
                statistic_dict["prioritize_clauses_min_cegar_iteration"].append(
                    prioritize_clauses_min_cegar_iteration)





            else:  # unsolvable with solvability file
                assign_values_to_unsolvable_problem(statistic_dict, record_fields)

        else:  # no solvability file
            assign_values_to_unsolvable_problem(statistic_dict, record_fields)


def get_fields_by_unsatcore_prioritize_clauses(json_obj, graph_type):
    suffix = "-" + "prioritizeClausesByUnsatCoreRank" + "-" + graph_type
    satisfiability = decode_satisfiability(float(read_a_json_field(json_obj, "satisfiability" + suffix)))
    cegar_iteration = int(float(read_a_json_field(json_obj, "cegarIterationNumber" + suffix)))
    cegar_iteration = 10800 if cegar_iteration == -1 else cegar_iteration
    solving_time = int(float(read_a_json_field(json_obj, "solvingTime" + suffix)))
    solving_time = 10800 if solving_time == -1 else solving_time / 1000
    return satisfiability, solving_time, cegar_iteration


def get_fields_by_unsatcore_threshold(json_obj, graph_type,
                                      threshold_list=[0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,
                                                      0.6]):
    measurement_list = ["satisfiability_list", "clause_number_after_pruning_list", "threshold_list",
                        "solving_time_list", "cegar_iteration_list"]
    satisfiability_dict_key_list = []
    for x in ["safe", "unsafe", "unknown"]:
        for measure in measurement_list:
            satisfiability_dict_key_list.append(x + "_" + measure)

    satisfiability_dict = {}
    assign_dict_key_empty_list(satisfiability_dict, satisfiability_dict_key_list)
    non_pruning_satisfiability = 10800
    non_pruning_solving_time = 10800
    non_pruning_cegar_iteration = 10800
    for t in threshold_list:
        suffix = "-" + graph_type + "-" + str(t)
        satisfiability = decode_satisfiability(float(read_a_json_field(json_obj, "satisfiability" + suffix)))
        clause_number_after_pruning = int(read_a_json_field(json_obj, "clauseNumberAfterPruning" + suffix))
        cegar_iteration = int(float(read_a_json_field(json_obj, "cegarIterationNumber" + suffix)))
        cegar_iteration = 10800 if cegar_iteration == -1 else cegar_iteration
        solving_time = int(float(read_a_json_field(json_obj, "solvingTime" + suffix)))
        solving_time = 10800 if solving_time == -1 else solving_time / 1000
        if t == 0:
            non_pruning_satisfiability = satisfiability
            non_pruning_solving_time = solving_time
            non_pruning_cegar_iteration = cegar_iteration

        if satisfiability == "safe":
            satisfiability_dict["safe_satisfiability_list"].append(satisfiability)
            satisfiability_dict["safe_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["safe_solving_time_list"].append(solving_time)
            satisfiability_dict["safe_threshold_list"].append(t)
            satisfiability_dict["safe_cegar_iteration_list"].append(cegar_iteration)

        elif satisfiability == "unsafe":
            satisfiability_dict["unsafe_satisfiability_list"].append(satisfiability)
            satisfiability_dict["unsafe_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["unsafe_solving_time_list"].append(solving_time)
            satisfiability_dict["unsafe_threshold_list"].append(t)
            satisfiability_dict["unsafe_cegar_iteration_list"].append(cegar_iteration)
        else:
            satisfiability_dict["unknown_satisfiability_list"].append(satisfiability)
            satisfiability_dict["unknown_clause_number_after_pruning_list"].append(clause_number_after_pruning)
            satisfiability_dict["unknown_solving_time_list"].append(solving_time)
            satisfiability_dict["unknown_threshold_list"].append(t)
            satisfiability_dict["unknown_cegar_iteration_list"].append(cegar_iteration)

    # we should always output unsafe results, since safe and unknown means nothing in pruned CHCs
    if len(satisfiability_dict["unsafe_satisfiability_list"]) != 0:
        return "unsafe", satisfiability_dict["unsafe_clause_number_after_pruning_list"], satisfiability_dict[
            "unsafe_threshold_list"], satisfiability_dict[
            "unsafe_solving_time_list"], satisfiability_dict[
            "unsafe_cegar_iteration_list"], non_pruning_satisfiability, non_pruning_solving_time, non_pruning_cegar_iteration
    elif len(satisfiability_dict["safe_satisfiability_list"]) != 0:
        return "safe", satisfiability_dict["safe_clause_number_after_pruning_list"], satisfiability_dict[
            "safe_threshold_list"], satisfiability_dict[
            "safe_solving_time_list"], satisfiability_dict[
            "safe_cegar_iteration_list"], non_pruning_satisfiability, non_pruning_solving_time, non_pruning_cegar_iteration
    else:
        return "unknown", satisfiability_dict["unknown_clause_number_after_pruning_list"], satisfiability_dict[
            "unknown_threshold_list"], satisfiability_dict[
            "unknown_solving_time_list"], satisfiability_dict[
            "unknown_cegar_iteration_list"], non_pruning_satisfiability, non_pruning_solving_time, non_pruning_cegar_iteration


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


def get_min_number_from_list(l, except_number):
    number_list = [x for x in l if x != except_number]
    if len(number_list) == 0:
        min_number = except_number
    else:
        min_number = min(number_list)
    if min_number == except_number:
        min_number = 10800
    return min_number


def get_improved_field(non_pruning_filed, field, except_number):
    if field != except_number:
        improved_field = non_pruning_filed - field
    else:
        improved_field = 10800
    return improved_field


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
    basic_info_columns = ["category_name", "total_number", "safe_number", "unsafe_number", "unknown_number",
                          "improved_solving_time_prioritize_clauses_number",
                          "improved_cegar_iteration_prioritize_clauses_number",
                          "improved_solving_time_threshold_number", "improved_cegar_iteartion_threshold_number"]
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
        # improved by prioritize
        improved_solving_time_prioritize_clauses = get_target_row_by_condition(data_dict, "category", c,
                                                                               "improved_solving_time_prioritize_clauses (s)")
        improved_cegar_iteration_prioritize_clauses = get_target_row_by_condition(data_dict, "category", c,
                                                                                  "improved_cegar_iteration_prioritize_clauses")
        improved_solving_time_list = [x for x in improved_solving_time_prioritize_clauses if x > 0]
        improved_cegar_iteration_list = [x for x in improved_cegar_iteration_prioritize_clauses if x > 0]
        category_dict["improved_solving_time_prioritize_clauses_number"].append(len(improved_solving_time_list))
        category_dict["improved_cegar_iteration_prioritize_clauses_number"].append(len(improved_cegar_iteration_list))
        # improved by threshold
        improved_solving_time_threshold = get_target_row_by_condition(data_dict, "category", c,
                                                                      "improved_solving_time_threshold (s)")
        improved_cegar_iteration_threshold = get_target_row_by_condition(data_dict, "category", c,
                                                                         "improved_cegar_iteartion_threshold")
        improved_solving_time_list = [x for x in improved_solving_time_threshold if x > 0]
        improved_cegar_iteration_list = [x for x in improved_cegar_iteration_threshold if x > 0]
        category_dict["improved_solving_time_threshold_number"].append(len(improved_solving_time_list))
        category_dict["improved_cegar_iteartion_threshold_number"].append(len(improved_cegar_iteration_list))


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


def get_summary_by_fields(data_dict, fields):
    summary = {}
    for f in fields:
        summary[f] = data_dict[f]

    summary = get_summary_by_satisfiability(summary, "unsafe")
    summary = get_summary_by_satisfiability(summary, "safe")
    return summary


def get_summary_by_satisfiability(summary, satisfiability="unsafe"):
    summary[satisfiability + "-common"] = [0 for x in summary["file_name"]]
    summary[satisfiability + "-unique-CDHG"] = [0 for x in summary["file_name"]]
    summary[satisfiability + "-unique-CG"] = [0 for x in summary["file_name"]]
    summary[satisfiability + "-total"] = [0 for x in summary["file_name"]]
    try:
        for c1, c2 in zip(summary["satisfiability-threshold-CDHG"], summary["satisfiability-threshold-CG"]):
            if c1 == c2 and c1 == satisfiability:
                summary[satisfiability + "-common"][0] += 1
            elif c1 == satisfiability and c2 != satisfiability:
                summary[satisfiability + "-unique-CDHG"][0] += 1
            elif c2 == satisfiability and c1 != satisfiability:
                summary[satisfiability + "-unique-CG"][0] += 1
    except:
        pass
    try:
        for c1, c2 in zip(summary["satisfiability-prioritize-clauses-CDHG"],
                          summary["satisfiability-prioritize-clauses-CG"]):
            if c1 == c2 and c1 == satisfiability:
                summary[satisfiability + "-common"][0] += 1
            elif c1 == satisfiability and c2 != satisfiability:
                summary[satisfiability + "-unique-CDHG"][0] += 1
            elif c2 == satisfiability and c1 != satisfiability:
                summary[satisfiability + "-unique-CG"][0] += 1
    except:
        pass
    summary[satisfiability + "-total"][0] = summary[satisfiability + "-unique-CDHG"][0] + \
                                            summary[satisfiability + "-unique-CG"][
                                                0] + summary[satisfiability + "-common"][0]

    return summary


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
