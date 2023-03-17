from src.utils import get_file_list, unzip_file, compress_file, make_dirct, read_a_json_field, \
    assign_dict_key_empty_list
import os
from src.collect_results.utils import read_files, read_json_file, get_sumary_folder, read_smt2_category
import pandas as pd
from tqdm import tqdm
from src.CONSTANTS import graph_types, benchmark_timeout
from src.benchmark_statistics.utils import get_fields_by_unsatcore_prioritize_clauses, \
    virtual_best_satisfiability_from_list, get_min_number_from_list, get_fields_by_unsatcore_threshold, \
    get_unsatcore_threshold_list, virtual_best_satisfiability_from_list_for_pruning, \
    virtual_best_solving_time_for_pruning, get_distinct_category_list


def main():
    summary_folder = get_sumary_folder(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data")

    golem_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-golem/train_data"
    z3_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-z3/train_data"

    eldarica_abstract_off_folder = golem_folder
    eldarica_abstract_off_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/unsatcore-linear-mixed/prioritize-normalized-rank/train_data"
    eldarica_abstract_off_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/unsatcore-linear-mixed/prioritize-only-rank/train_data"
    eldarica_abstract_off_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/unsatcore-linear-mixed/threshold-rank/train_data"
    eldarica_abstract_off_folder_pruning_score_folder = ""

    full_file_folder = golem_folder

    solver_variation_folders_dict = {"golem": golem_folder, "z3": z3_folder,
                                     "eldarica_abstract_off": eldarica_abstract_off_folder,
                                     "eldarica_abstract_off_prioritizing_SEH": eldarica_abstract_off_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_off_prioritizing_rank": eldarica_abstract_off_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_off_pruning_rank": eldarica_abstract_off_folder_pruning_rank_folder,
                                     "eldarica_abstract_off_pruning_score": eldarica_abstract_off_folder_pruning_score_folder}

    solvability_dict = read_solvability_cross_solvers_to_dict(full_file_folder, solver_variation_folders_dict)

    category_dict = category_summary_for_solvability_dict(solvability_dict, solver_variation_folders_dict)

    # write to excel
    with pd.ExcelWriter(summary_folder + "/" + "statistics_split_clauses_1.xlsx") as writer:
        pd.DataFrame(pd.DataFrame(solvability_dict)).to_excel(writer, sheet_name="data")
        pd.DataFrame(pd.DataFrame(category_dict)).to_excel(writer, sheet_name="category_summary")


def category_summary_for_solvability_dict(solvability_dict, solver_variation_folders_dict):
    categories = get_distinct_category_list(solvability_dict["category"])
    measurements = ["safe", "unsafe", "unknown","solving_time"]

    # get column names
    columns = ["category"]
    for solver in solver_variation_folders_dict:
        for s in measurements:
            if "prioritizing" in solver or "pruning" in solver:
                columns.append("vb_" + solver + "_" + s)
            else:
                columns.append(solver + "_" + s)

    # initialize dict
    category_dict = {}
    assign_dict_key_empty_list(category_dict, columns)

    # compute each column
    for c in categories:
        category_dict["category"].append(c)
        for m in measurements:
            for solver in solver_variation_folders_dict:
                if "prioritizing" in solver or "pruning" in solver:
                    count_satisfiability(c, m, solvability_dict, category_dict, "vb_" + solver)
                    sum_solving_time(c, solvability_dict, category_dict, "vb_" + solver)
                else:
                    count_satisfiability(c, m, solvability_dict, category_dict, solver)
                    sum_solving_time(c, solvability_dict, category_dict, solver)
    # add total row
    category_dict["category"].append("total")
    for m in measurements:
        for solver in solver_variation_folders_dict:
            if "prioritizing" in solver or "pruning" in solver:
                category_dict["vb_" + solver + "_" + m].append(sum(category_dict["vb_" + solver + "_" + m]))
            else:
                category_dict[solver + "_" + m].append(sum(category_dict[solver + "_" + m]))

    return category_dict


def count_satisfiability(c, s, solvability_dict, category_dict, solver):
    count = 0
    for ca, sa in zip(solvability_dict["category"], solvability_dict[solver + "_satisfiability"]):
        if c in ca and s == sa:
            count += 1
        category_dict[solver + "_" + s].append(count)

def sum_solving_time(c,solvability_dict, category_dict, solver):
    solving_time=0
    for ca, st in zip(solvability_dict["category"], solvability_dict[solver + "_solving_time"]):
        if c in ca:
            solving_time+=st
    category_dict[solver + "_solving_time"].append(solving_time)

def read_solvability_cross_solvers_to_dict(full_file_folder, solver_variation_folders_dict):
    # decide record fields
    record_fields = []
    other_fields = ["file_name"]
    smt_measurements = ["file_size", "file_size_h", "category"]
    solver_variations = solver_variation_folders_dict.keys()
    measurements = ["satisfiability", "solving_time"]
    for sv in solver_variations:
        for m in measurements:
            record_fields.append(sv + "_" + m)
            if "prioritizing" in sv or "pruning" in sv:
                record_fields.append("vb_" + sv + "_" + m)
    record_fields = other_fields + smt_measurements + record_fields

    # initialize solvability dict
    solvability_dict = {}
    assign_dict_key_empty_list(solvability_dict, record_fields)

    # read fixed fields
    file_list = get_file_list(full_file_folder, "smt2")
    for sm in smt_measurements:
        solvability_dict[sm] = [x[sm] for x in
                                read_files(file_list, file_type="", read_function=read_smt2_category)]

    # read solvabilities by file
    for file in tqdm(file_list, desc="read files"):
        file_basename = os.path.basename(file)
        solvability_dict["file_name"].append(file_basename[:-len(".zip")])
        for solver_variation in solver_variations:
            # if solver_variation_folders_dict[solver_variation] != "":
            if "golem" in solver_variation:
                json_file_suffix = "golem-solvability.JSON"
            elif "z3" in solver_variation:
                json_file_suffix = "z3-solvability.JSON"
            elif "eldarica_abstract_off" == solver_variation:
                json_file_suffix = "golem-solvability.JSON"  # todo check this
            else:
                json_file_suffix = "solvability.JSON"

            solvability_object_list = read_files(
                [os.path.join(solver_variation_folders_dict[solver_variation], file_basename)],
                file_type=json_file_suffix,
                read_function=read_json_file, disable_tqdm=True)
            for object in solvability_object_list:
                if "prioritizing" in solver_variation:  # read from prioritizing eldarica variations
                    if len(object) > 1:  # has solvability file
                        satisfiability_CDHG, solving_time_CDHG, cegar_iteration_CDHG = get_fields_by_unsatcore_prioritize_clauses(
                            object, "CDHG")
                        satisfiability_CG, solving_time_CG, cegar_iteration_CG = get_fields_by_unsatcore_prioritize_clauses(
                            object, "CG")
                        # virtual best of graphs
                        virtual_best_satisfiability_graphs = virtual_best_satisfiability_from_list(
                            [satisfiability_CDHG, satisfiability_CG])
                        virtual_best_solving_time_graphs = get_min_number_from_list(
                            [solving_time_CDHG, solving_time_CG], -0.001)

                        satisfiability, solving_time = mask_results_by_benchmark_timeout(virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs)
                        solvability_dict[solver_variation + "_" + "satisfiability"].append(satisfiability)
                        solvability_dict[solver_variation + "_" + "solving_time"].append(solving_time)

                    else:  # no solvability file
                        for m in measurements:
                            solvability_dict[solver_variation + "_" + m].append("miss info")
                        virtual_best_satisfiability_graphs = "unknown"
                        virtual_best_solving_time_graphs = benchmark_timeout

                    # virtual best of eldarica
                    virtual_best_cross_eldarica_variation(solver_variation, solvability_dict,
                                                          virtual_best_satisfiability_graphs,
                                                          virtual_best_solving_time_graphs, measurements,
                                                          "prioritizing")

                elif "pruning" in solver_variation:  # read from pruning eldarica variations
                    if len(object) > 1:  # has solvability file
                        threshold_list = get_unsatcore_threshold_list()
                        satisfiability_CDHG, clause_number_after_pruning_list_CDHG, threshold_list_CDHG, solving_time_list_CDHG, cegar_number_list_CDHG, \
                            non_pruning_satisfiability_CDHG, non_pruning_solving_time_CDHG, non_pruning_cegar_iteration_CDHG = get_fields_by_unsatcore_threshold(
                            object, "CDHG", threshold_list=threshold_list)
                        satisfiability_CG, clause_number_after_pruning_list_CG, threshold_list_CG, solving_time_list_CG, cegar_number_list_CG, \
                            non_pruning_satisfiability_CG, non_pruning_solving_time_CG, non_pruning_cegar_iteration_CG = get_fields_by_unsatcore_threshold(
                            object, "CG", threshold_list=threshold_list)
                        virtual_best_satisfiability_graphs = virtual_best_satisfiability_from_list_for_pruning(
                            [satisfiability_CDHG, satisfiability_CG])
                        virtual_best_solving_time_graphs, virtual_best_threshold_graphs, virtual_best_clause_number_graphs = virtual_best_solving_time_for_pruning(
                            satisfiability_CDHG, satisfiability_CG,
                            solving_time_list_CDHG, solving_time_list_CG, threshold_list_CDHG, threshold_list_CG,
                            clause_number_after_pruning_list_CDHG, clause_number_after_pruning_list_CG, -0.001)
                        # compound field = field[virtual_best_threshold_graphs][virtual_best_clause_number_graphs]

                        satisfiability, solving_time = mask_results_by_benchmark_timeout(
                            virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs)
                        solvability_dict[solver_variation + "_" + "satisfiability"].append(str(satisfiability) + "[" + str(virtual_best_threshold_graphs) + "]" + "[" + str(
                                    virtual_best_clause_number_graphs) + "]")
                        solvability_dict[solver_variation + "_" + "solving_time"].append(str(solving_time) + "[" + str(virtual_best_threshold_graphs) + "]" + "[" + str(
                                    virtual_best_clause_number_graphs) + "]")

                    else:  # no solvability file
                        for m in measurements:
                            solvability_dict[solver_variation + "_" + m].append("miss info")
                        virtual_best_satisfiability_graphs = "unknown"
                        virtual_best_solving_time_graphs = benchmark_timeout
                    # virtual best of eldarica
                    virtual_best_cross_eldarica_variation(solver_variation, solvability_dict,
                                                          virtual_best_satisfiability_graphs,
                                                          virtual_best_solving_time_graphs, measurements,
                                                          "pruning")
                else:  # read from standard solvers
                    satisfiability = read_a_json_field(object, "satisfiability")
                    solving_time = float(read_a_json_field(object, "solving_time"))
                    satisfiability, solving_time = mask_results_by_benchmark_timeout(satisfiability, solving_time)
                    solvability_dict[solver_variation + "_" + "satisfiability"].append(satisfiability)
                    solvability_dict[solver_variation + "_" + "solving_time"].append(solving_time)


    for k in solvability_dict:
        print(k, len(solvability_dict[k]))
    return solvability_dict


def virtual_best_cross_eldarica_variation(solver_variation, solvability_dict, virtual_best_satisfiability_graphs,
                                          virtual_best_solving_time_graphs, measurements, option):
    eldarica_base_variation = solver_variation[:solver_variation.find("_" + option)]
    satisfiability_abstract = solvability_dict[eldarica_base_variation + "_satisfiability"][-1]
    solving_time_abstract = solvability_dict[eldarica_base_variation + "_solving_time"][-1]
    virtual_best_satisfiability = virtual_best_satisfiability_from_list(
        [virtual_best_satisfiability_graphs, satisfiability_abstract])
    virtual_best_solving_time = get_min_number_from_list(
        [virtual_best_solving_time_graphs, float(solving_time_abstract)], -0.001)

    satisfiability, solving_time = mask_results_by_benchmark_timeout(virtual_best_satisfiability,
                                                                     virtual_best_solving_time)
    solvability_dict["vb_" +solver_variation + "_" + "satisfiability"].append(satisfiability)
    solvability_dict["vb_" +solver_variation + "_" + "solving_time"].append(solving_time)


def mask_results_by_benchmark_timeout(satisfiability, solving_time):
    if solving_time > benchmark_timeout:
        solving_time = benchmark_timeout
        satisfiability = "unknown"
    return satisfiability, solving_time


if __name__ == '__main__':
    main()
