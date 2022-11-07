import os.path
import json
from utils import read_files, get_sumary_folder,read_json_file
from src.utils import get_file_list, make_dirct
import pandas as pd
from statistics import mean
from src.plots import plot_cactus


def main():
    folder = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/linear_dataset/train_data"
    # get abstract_option_list
    abstract_option_list = get_abstract_option_list()

    # build solvability_summary_by_abstract_option
    solvability_summary_by_abstract_option = get_solvability_summary_by_abstract_option(abstract_option_list, folder)

    write_solvability_summary_to_file(folder, solvability_summary_by_abstract_option, key_word="")

    plot_cactus(get_sumary_folder(folder), solvability_summary_by_abstract_option)

    # todo write to latex

    print("abstract_option_list", len(solvability_summary_by_abstract_option))
    for x in solvability_summary_by_abstract_option:
        print(x, solvability_summary_by_abstract_option[x])



def write_solvability_summary_to_file(folder, solvability_summary, key_word=""):
    # write to json
    output = {}
    summary_folder = get_sumary_folder(folder)
    summary_json_file_name = summary_folder + "/solvability_summary.JSON"
    for f in solvability_summary:
        sub_fields = {}
        for k in solvability_summary[f]:
            if key_word in k:
                sub_fields.update({k: solvability_summary[f][k]})
        output.update({f: sub_fields})
    with open(summary_json_file_name, 'w') as f:
        json.dump(output, f, indent=4, sort_keys=True)

    # write to spreadsheet
    option_list = []
    solvable_number_list = []
    unique_solved_number_list = []
    safe_number_list = []
    unsafe_number_list = []
    average_solving_time_list = []
    for f in solvability_summary:
        option_list.append(f)
        solvable_number_list.append(solvability_summary[f]["solvable_number"])
        unique_solved_number_list.append(solvability_summary[f]["unique_solvable_number"])
        safe_number = sum(solvability_summary[f]["satisfiability_list"])
        safe_number_list.append(safe_number)
        unsafe_number_list.append(len(solvability_summary[f]["satisfiability_list"]) - safe_number)
        _solving_time_list= [0] if len(solvability_summary[f]["solvingTime_list"])==0 else solvability_summary[f]["solvingTime_list"]
        average_solving_time_list.append(mean(_solving_time_list))

    df = pd.DataFrame(
        dict(Options=option_list, Solvable_number=solvable_number_list,
             Average_solving_time_ms=average_solving_time_list,
             Unique_solved_number=unique_solved_number_list, Safe_number=safe_number_list,
             Unsafe_number=unsafe_number_list))
    df.to_excel(summary_folder + "/solvability_summary.xlsx")


def get_solvability_summary_by_abstract_option(abstract_option_list, folder):
    file_list = get_file_list(folder, "smt2")
    solvability_object_list = read_files(file_list,file_type="solvability.JSON",read_function=read_json_file)

    measurement_list = ["solvingTime", "cegarIterationNumber", "predicateGeneratorTime", "satisfiability"]
    # change getSolvability and CEGAR in Eldarica to collect generatedPredicateNumber and averagePredicateSize

    solvability_summary_by_abstract_option = {op: dict({m + "_list": [] for m in measurement_list},
                                                       **{"solvable_number": 0, "solvable_list": [],
                                                          "unique_solvable_number": 0, "unique_solvable_list": []}) for
                                              op in abstract_option_list}

    # fill in solvability_summary_by_abstract_option by iterating the solvability list
    for solvability_object in solvability_object_list:
        for op in solvability_summary_by_abstract_option:
            measurement_dict = {m: int(solvability_object[m + "_" + op][0]) for m in measurement_list}
            if measurement_dict["solvingTime"] != 10800000:
                solvability_summary_by_abstract_option[op]["solvable_number"] += 1
                solvability_summary_by_abstract_option[op]["solvable_list"].append(
                    os.path.basename(solvability_object["file_name"]))
                for m in measurement_list:
                    solvability_summary_by_abstract_option[op][m + "_list"].append(measurement_dict[m])

        # todo check this implementation when have the whole dataset
        # get unique solved list by differernt abstract option
        for i in solvability_summary_by_abstract_option:
            solvable_set_from_other_option = []
            for j in solvability_summary_by_abstract_option:
                if j != i:
                    solvable_set_from_other_option = solvable_set_from_other_option + \
                                                     solvability_summary_by_abstract_option[j][
                                                         "solvable_list"]
            solvable_set_from_other_option = list(set(solvable_set_from_other_option))
            unique_solved_list = set(solvability_summary_by_abstract_option[i]["solvable_list"]).difference(
                set(solvable_set_from_other_option))
            if len(unique_solved_list) != 0:
                solvability_summary_by_abstract_option[i]["unique_solvable_number"] = len(unique_solved_list)
                solvability_summary_by_abstract_option[i]["unique_solvable_list"] = list(unique_solved_list)

    return solvability_summary_by_abstract_option


def get_abstract_option_list():
    abstract_option_list = []
    combOption = ["off", "union", "random"]
    manual_abstract_options = ["Term", "Octagon", "RelationalEqs", "RelationalIneqs"]
    predicted_abstract_options = ["PredictedCG", "PredictedCDHG"]
    other_abstract_options = ["Empty", "Unlabeled", "Random", "Mined"]
    cost_type = ["cost_same", "cost_shape", "cost_logit"]
    split_clause_op = ["splitClauses_1"]  # "splitClauses_0"
    graph_types = ["CG", "CDHG"]
    explorationRate = [0.5]

    for sc in split_clause_op:
        for cb in combOption:
            if cb == "off":
                for ao in manual_abstract_options + other_abstract_options:  # existed templates with same cost
                    abstract_option_list.append(
                        ao + "_" + "CDHG" + "_" + cb + "_" + "0.0" + "_" + sc + "_" + "cost_same")
                for ao in predicted_abstract_options:  # predicted templates with differernt cost
                    for c in cost_type:
                        if "PredictedCG" not in ao:
                            abstract_option_list.append(
                                ao + "_" + "CDHG" + "_" + cb + "_" + "0.0" + "_" + sc + "_" + c)
                        else:
                            abstract_option_list.append(
                                ao + "_" + "CG" + "_" + cb + "_" + "0.0" + "_" + sc + "_" + c)
            elif cb == "union":
                for ao in manual_abstract_options:
                    for g in graph_types:
                        for c in cost_type:
                            abstract_option_list.append(
                                ao + "_" + g + "_" + cb + "_" + "0.0" + "_" + sc + "_" + c)
            elif cb == "random":
                for ao in manual_abstract_options:
                    for g in graph_types:
                        for c in cost_type:
                            for e in explorationRate:
                                abstract_option_list.append(
                                    ao + "_" + g + "_" + cb + "_" + str(e) + "_" + sc + "_" + c)

    return abstract_option_list


if __name__ == '__main__':
    main()
