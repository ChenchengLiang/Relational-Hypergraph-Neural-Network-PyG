import sys

from src.utils import get_file_list, unzip_file, compress_file, make_dirct, read_a_json_field, \
    assign_dict_key_empty_list
import os
from src.collect_results.utils import read_files, read_json_file, get_sumary_folder, read_smt2_category, \
    copy_relative_files
import pandas as pd
from tqdm import tqdm
from src.CONSTANTS import graph_types, benchmark_timeout, eldarica_abstract_options, threshold_list
from src.benchmark_statistics.utils import get_fields_by_unsatcore_prioritize_clauses, \
    virtual_best_satisfiability_from_list, get_min_number_from_list, get_fields_by_unsatcore_threshold, \
    get_unsatcore_threshold_list, virtual_best_satisfiability_from_list_for_pruning, \
    virtual_best_solving_time_for_pruning, get_distinct_category_list, get_target_row_by_condition


def main():
    golem_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-golem/train_data"
    z3_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-z3/train_data"

    eldarica_abstract_off_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-off/train_data"
    eldarica_abstract_off_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-off-prioritize-SEH/train_data"
    eldarica_abstract_off_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-off-prioritize-only-rank/train_data"
    eldarica_abstract_off_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-off-pruning-threshold-rank/train_data"
    eldarica_abstract_off_folder_pruning_score_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-off-pruning-normalized-scores/train_data"

    eldarica_abstract_term_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-term/train_data"
    eldarica_abstract_term_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-term-prioritize-SEH/train_data"
    eldarica_abstract_term_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-term-prioritize-only-rank/train_data"
    eldarica_abstract_term_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-term-pruning-threshold-rank/train_data"
    eldarica_abstract_term_folder_pruning_score_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-term-pruning-normalized-scores/train_data"

    eldarica_abstract_oct_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-oct/train_data"
    eldarica_abstract_oct_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-oct-prioritize-SEH/train_data"
    eldarica_abstract_oct_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-oct-prioritize-only-rank/train_data"
    eldarica_abstract_oct_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-oct-pruning-threshold-rank/train_data"
    eldarica_abstract_oct_folder_pruning_score_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-oct-pruning-normalized-scores/train_data"

    eldarica_abstract_relEqs_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relEqs/train_data"
    eldarica_abstract_relEqs_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relEqs-prioritize-SEH/train_data"
    eldarica_abstract_relEqs_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relEqs-prioritize-only-rank/train_data"
    eldarica_abstract_relEqs_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relEqs-pruning-threshold-rank/train_data"
    eldarica_abstract_relEqs_folder_pruning_score_folder = ""#running need rerun unknown part-5-237

    eldarica_abstract_relIneqs_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relIneqs/train_data"
    eldarica_abstract_relIneqs_folder_prioritizing_SEH_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relIneqs-prioritize-SEH/train_data"
    eldarica_abstract_relIneqs_folder_prioritizing_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relIneqs-prioritize-only-rank/train_data"
    eldarica_abstract_relIneqs_folder_pruning_rank_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-eldarica-abstract-relIneqs-pruning-threshold-rank/train_data"
    eldarica_abstract_relIneqs_folder_pruning_score_folder = ""

    # golem_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-golem/test_data"
    # z3_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-z3/test_data"
    #
    # eldarica_abstract_off_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-test/test_data"
    # eldarica_abstract_off_folder_prioritizing_SEH_folder = ""
    # eldarica_abstract_off_folder_prioritizing_rank_folder = ""
    # eldarica_abstract_off_folder_pruning_rank_folder = ""
    # eldarica_abstract_off_folder_pruning_score_folder = ""
    #
    # eldarica_abstract_term_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-test/test_data"
    # eldarica_abstract_term_folder_prioritizing_SEH_folder = ""
    # eldarica_abstract_term_folder_prioritizing_rank_folder = ""
    # eldarica_abstract_term_folder_pruning_rank_folder = ""
    # eldarica_abstract_term_folder_pruning_score_folder = ""
    #
    # eldarica_abstract_oct_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-test/test_data"
    # eldarica_abstract_oct_folder_prioritizing_SEH_folder = ""
    # eldarica_abstract_oct_folder_prioritizing_rank_folder = ""
    # eldarica_abstract_oct_folder_pruning_rank_folder = ""
    # eldarica_abstract_oct_folder_pruning_score_folder = ""
    #
    # eldarica_abstract_relEqs_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-test/test_data"
    # eldarica_abstract_relEqs_folder_prioritizing_SEH_folder = ""
    # eldarica_abstract_relEqs_folder_prioritizing_rank_folder = ""
    # eldarica_abstract_relEqs_folder_pruning_rank_folder = ""
    # eldarica_abstract_relEqs_folder_pruning_score_folder = ""  # running need rerun unknown part-5-237
    #
    # eldarica_abstract_relIneqs_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/solvability-linear-test/test_data"
    # eldarica_abstract_relIneqs_folder_prioritizing_SEH_folder = ""
    # eldarica_abstract_relIneqs_folder_prioritizing_rank_folder = ""
    # eldarica_abstract_relIneqs_folder_pruning_rank_folder = ""
    # eldarica_abstract_relIneqs_folder_pruning_score_folder = ""

    eldarica_symex_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/symex-test"
    eldarica_symex_folder_original = os.path.join(eldarica_symex_folder, "original")
    eldarica_symex_folder_CDHG = os.path.join(eldarica_symex_folder, "CDHG")
    eldarica_symex_folder_CG = os.path.join(eldarica_symex_folder, "CG")

    full_file_folder = golem_folder
    summary_folder = get_sumary_folder(os.path.dirname(os.path.dirname(golem_folder)) + "/data")

    solver_variation_folders_dict = {"golem": golem_folder, "z3": z3_folder,
                                     "eldarica_symex_original": eldarica_symex_folder_original,
                                     "eldarica_symex_CDHG": eldarica_symex_folder_CDHG,
                                     "eldarica_symex_CG": eldarica_symex_folder_CG,
                                     "eldarica_abstract_off": eldarica_abstract_off_folder,
                                     "eldarica_abstract_off_prioritizing_SEH": eldarica_abstract_off_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_off_prioritizing_rank": eldarica_abstract_off_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_off_pruning_rank": eldarica_abstract_off_folder_pruning_rank_folder,
                                     "eldarica_abstract_off_pruning_score": eldarica_abstract_off_folder_pruning_score_folder,
                                     "eldarica_abstract_term": eldarica_abstract_term_folder,
                                     "eldarica_abstract_term_prioritizing_SEH": eldarica_abstract_term_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_term_prioritizing_rank": eldarica_abstract_term_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_term_pruning_rank": eldarica_abstract_term_folder_pruning_rank_folder,
                                     "eldarica_abstract_term_pruning_score": eldarica_abstract_term_folder_pruning_score_folder,
                                     "eldarica_abstract_oct": eldarica_abstract_oct_folder,
                                     "eldarica_abstract_oct_prioritizing_SEH": eldarica_abstract_oct_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_oct_prioritizing_rank": eldarica_abstract_oct_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_oct_pruning_rank": eldarica_abstract_oct_folder_pruning_rank_folder,
                                     "eldarica_abstract_oct_pruning_score": eldarica_abstract_oct_folder_pruning_score_folder,
                                     "eldarica_abstract_relEqs": eldarica_abstract_relEqs_folder,
                                     "eldarica_abstract_relEqs_prioritizing_SEH": eldarica_abstract_relEqs_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_relEqs_prioritizing_rank": eldarica_abstract_relEqs_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_relEqs_pruning_rank": eldarica_abstract_relEqs_folder_pruning_rank_folder,
                                     "eldarica_abstract_relEqs_pruning_score": eldarica_abstract_relEqs_folder_pruning_score_folder,
                                     "eldarica_abstract_relIneqs": eldarica_abstract_relIneqs_folder,
                                     "eldarica_abstract_relIneqs_prioritizing_SEH": eldarica_abstract_relIneqs_folder_prioritizing_SEH_folder,
                                     "eldarica_abstract_relIneqs_prioritizing_rank": eldarica_abstract_relIneqs_folder_prioritizing_rank_folder,
                                     "eldarica_abstract_relIneqs_pruning_rank": eldarica_abstract_relIneqs_folder_pruning_rank_folder,
                                     "eldarica_abstract_relIneqs_pruning_score": eldarica_abstract_relIneqs_folder_pruning_score_folder
                                     }

    solvability_dict = read_solvability_cross_solvers_to_dict(full_file_folder, solver_variation_folders_dict)

    category_dict = category_summary_for_solvability_dict(solvability_dict, solver_variation_folders_dict)

    # write to excel
    with pd.ExcelWriter(summary_folder + "/" + "statistics_split_clauses_1.xlsx") as writer:
        pd.DataFrame(pd.DataFrame(solvability_dict)).to_excel(writer, sheet_name="data")
        pd.DataFrame(pd.DataFrame(category_dict)).to_excel(writer, sheet_name="category_summary")
        pd.DataFrame(pd.DataFrame(category_dict)).transpose().to_excel(writer, sheet_name="category_summary_transpose")


def category_summary_for_solvability_dict(solvability_dict, solver_variation_folders_dict):
    categories = get_distinct_category_list(solvability_dict["category"])
    measurements = ["safe", "unsafe", "unknown", "miss info", "solving_time"]
    comparison_solver_list = ["vb"]
    for solver in solver_variation_folders_dict:
        if "prioritizing" in solver or "pruning" in solver:
            comparison_solver_list.append("vb_" + solver)
        elif "eldarica_symex_original" in solver:
            comparison_solver_list.append("eldarica_symex_original")
            comparison_solver_list.append("vb_eldarica_symex_prioritize")
            comparison_solver_list.append("vb_eldarica_symex")
        elif solver in ["eldarica_symex_CDHG", "eldarica_symex_CG"]:
            pass
        else:
            comparison_solver_list.append(solver)

    # get column names
    columns = ["category"]
    columns.append("number_predicted")
    for solver in comparison_solver_list:
        for s in measurements:
            columns.append(solver + "_" + s)

    # initialize dict
    category_dict = {}
    assign_dict_key_empty_list(category_dict, columns)

    # compute each column
    for c in categories:
        category_dict["category"].append(c)
        for m in measurements:
            for solver in comparison_solver_list:
                count_satisfiability_and_sum_solving_time(c, m, solvability_dict, category_dict, solver)

    # get number of predicted
    for c in categories:
        count = 0
        for ca, sa in zip(solvability_dict["category"],
                          solvability_dict["eldarica_abstract_off_prioritizing_SEH_satisfiability"]):
            if c in ca and sa != "miss info":
                count += 1
        category_dict["number_predicted"].append(count)

    # compute lcr
    lcr_comparison_list = ["vb_eldarica", "vb_eldarica_original"]
    # get cross solver comparison list
    for solver in [x for x in solver_variation_folders_dict if x not in ["z3", "golem"]]:
        if "prioritizing" in solver or "pruning" in solver:
            lcr_comparison_list.append("vb_" + solver)
        else:
            lcr_comparison_list.append(solver)
    lcr_solver_sets = [["z3", "golem"] + [e] for e in lcr_comparison_list]
    # get eldarica comparison list
    for a in eldarica_abstract_options + ["off"]:
        lcr_solver_sets.append(["eldarica_abstract_" + a] + ["vb_eldarica_abstract_" + a + "_" + "prioritizing",
                                                             "vb_eldarica_abstract_" + a + "_" + "pruning"])

    for i, solver_set in enumerate(lcr_solver_sets):
        lcr_dict = compute_lcr_for_one_set_of_solvers(solvability_dict, category_dict, solver_set)
        for lcr in lcr_dict:
            category_dict["[" + str(i) + "]" + lcr] = lcr_dict[lcr]

    # add total row
    category_dict["category"].append("total")
    category_dict["number_predicted"].append(sum(category_dict["number_predicted"]))
    for solver in comparison_solver_list:
        for m in measurements:
            category_dict[solver + "_" + m].append(sum(category_dict[solver + "_" + m]))

    # add total row for lcr
    for i, solver_set in enumerate(lcr_solver_sets):
        for m in [" lcr_n ", " lcr_c "]:
            for solver in solver_set:
                category_dict["[" + str(i) + "]" + m + solver].append(
                    sum(category_dict["[" + str(i) + "]" + m + solver]))

    # add total-lcr row
    category_dict["category"].append("total-lcr")
    category_dict["number_predicted"].append("-")
    for solver in comparison_solver_list:
        for m in measurements:
            category_dict[solver + "_" + m].append("-")

    # compute lcr
    for i, solver_set in enumerate(lcr_solver_sets):
        for solver in solver_set:  # lcr column
            # get vb_satisfiability_list and vb_solving_time_list
            vb_satisfiability_list, vb_solving_time_list = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
                solvability_dict, solver_set)
            # get vb_satisfiability_list and vb_solving_time_list from other solvers
            other_solvers = solver_set.copy()
            other_solvers.remove(solver)
            vb_satisfiability_list_other_solvers, vb_solving_time_list_other_solvers = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
                solvability_dict, other_solvers)
            vbssn, vbssc = compute_vbss("", solvability_dict, vb_satisfiability_list, vb_solving_time_list)
            vbssn_other_solvers, vbssc_other_solvers = compute_vbss("", solvability_dict,
                                                                    vb_satisfiability_list_other_solvers,
                                                                    vb_solving_time_list_other_solvers)

            lcr_n = 1 - (vbssn_other_solvers / vbssn)
            lcr_c = 1 - (vbssc / vbssc_other_solvers)
            category_dict["[" + str(i) + "]" + " lcr_n " + solver].append(lcr_n)
            category_dict["[" + str(i) + "]" + " lcr_c " + solver].append(lcr_c)

    # print category_dict column number
    for k in category_dict:
        print(k, len(category_dict[k]))

    return category_dict


def compute_lcr_for_one_set_of_solvers(solvability_dict, category_dict, cross_solvers_list):
    # add largest contribution rank column for each solver
    lcr_dict = {}
    for m in [" lcr_n ", " lcr_c "]:
        for s in cross_solvers_list:
            lcr_dict[m + s] = []

    # compute lcr
    for solver in cross_solvers_list:  # lcr column
        # get vb_satisfiability_list and vb_solving_time_list
        vb_satisfiability_list, vb_solving_time_list = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
            solvability_dict, cross_solvers_list)
        # get vb_satisfiability_list and vb_solving_time_list from other solvers
        other_solvers = cross_solvers_list.copy()
        other_solvers.remove(solver)
        vb_satisfiability_list_other_solvers, vb_solving_time_list_other_solvers = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
            solvability_dict, other_solvers)

        for c in category_dict["category"]:
            vbssn, vbssc = compute_vbss(c, solvability_dict, vb_satisfiability_list, vb_solving_time_list)
            vbssn_other_solvers, vbssc_other_solvers = compute_vbss(c, solvability_dict,
                                                                    vb_satisfiability_list_other_solvers,
                                                                    vb_solving_time_list_other_solvers)

            lcr_n = 1 - (vbssn_other_solvers / vbssn)
            lcr_c = 1 - (vbssc / vbssc_other_solvers)

            # print(c, "vb:", vbssn, "remove " + solver + ":", vbssn_other_solvers,"lcr_n:", lcr_n)

            lcr_dict[" lcr_n " + solver].append(lcr_n)
            lcr_dict[" lcr_c " + solver].append(lcr_c)

    return lcr_dict


def compute_vbss(c, solvability_dict, vb_satisfiability_list, vb_solving_time_list):
    vbssn = 0
    vbssc = 0
    for category, vb_satisfiability, vb_solving_time in zip(solvability_dict["category"], vb_satisfiability_list,
                                                            vb_solving_time_list):
        if c in category and vb_satisfiability in ["safe", "unsafe"]:
            vbssn += 1
        if c in category:
            vbssc += vb_solving_time
    return vbssn, vbssc


def count_satisfiability_and_sum_solving_time(c, m, solvability_dict, category_dict, solver):
    count = 0
    solving_time = 0
    for ca, sa, st in zip(solvability_dict["category"], solvability_dict[solver + "_satisfiability"],
                          solvability_dict[solver + "_solving_time"]):
        if c in ca and m == sa:
            count += 1
        if c in ca:
            solving_time += st
    if "solving_time" == m:
        category_dict[solver + "_" + m].append(solving_time)
    else:
        category_dict[solver + "_" + m].append(count)


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
        if "eldarica_symex_original" in sv:
            for m in measurements:
                record_fields.append("vb_eldarica_symex_prioritize" + "_" + m)
            for m in measurements:
                record_fields.append("vb_eldarica_symex" + "_" + m)
        if sv in ["z3", "golem"]:
            for m in measurements:
                record_fields.append(sv + "_pruning_" + m)
    record_fields = other_fields + smt_measurements + record_fields

    # initialize solvability dict
    solvability_dict = {}
    assign_dict_key_empty_list(solvability_dict, record_fields)

    # read pruning solvability from standard solvers
    read_pruning_solvability_for_standard_solvers(solvability_dict, full_file_folder, measurements)

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
            elif solver_variation in ["eldarica_abstract_off"] + ["eldarica_abstract_" + x for x in
                                                                  eldarica_abstract_options] + [
                "eldarica_symex_original"]:
                json_file_suffix = "eld-solvability.JSON"
            elif solver_variation in ["eldarica_symex_CDHG", "eldarica_symex_CG"]:
                json_file_suffix = "simplified.smt2.eld-solvability.JSON"
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

                        virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs = mask_results_by_benchmark_timeout(
                            virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs)

                        solvability_dict[solver_variation + "_" + "satisfiability"].append(
                            virtual_best_satisfiability_graphs)
                        solvability_dict[solver_variation + "_" + "solving_time"].append(
                            virtual_best_solving_time_graphs)

                    else:  # no solvability file
                        solvability_dict[solver_variation + "_satisfiability"].append("miss info")
                        solvability_dict[solver_variation + "_solving_time"].append(benchmark_timeout)
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

                        virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs = mask_results_by_benchmark_timeout(
                            virtual_best_satisfiability_graphs, virtual_best_solving_time_graphs)

                        solvability_dict[solver_variation + "_" + "satisfiability"].append(
                            str(virtual_best_satisfiability_graphs) + "[" + str(
                                virtual_best_threshold_graphs) + "]" + "[" + str(
                                virtual_best_clause_number_graphs) + "]")
                        solvability_dict[solver_variation + "_" + "solving_time"].append(
                            str(virtual_best_solving_time_graphs) + "[" + str(
                                virtual_best_threshold_graphs) + "]" + "[" + str(
                                virtual_best_clause_number_graphs) + "]")

                    else:  # no solvability file
                        solvability_dict[solver_variation + "_satisfiability"].append("miss info")
                        solvability_dict[solver_variation + "_solving_time"].append(benchmark_timeout)
                        virtual_best_satisfiability_graphs = "unknown"
                        virtual_best_solving_time_graphs = benchmark_timeout

                    # virtual best of eldarica
                    virtual_best_cross_eldarica_variation(solver_variation, solvability_dict,
                                                          virtual_best_satisfiability_graphs,
                                                          virtual_best_solving_time_graphs, measurements,
                                                          "pruning")

                else:  # read from standard solvers
                    if len(object) > 1:  # has solvability file
                        satisfiability = read_a_json_field(object, "satisfiability")
                        solving_time = benchmark_timeout if satisfiability == "unknown" else float(
                            read_a_json_field(object, "solving_time"))

                        satisfiability, solving_time = mask_results_by_benchmark_timeout(satisfiability, solving_time)
                        solvability_dict[solver_variation + "_" + "satisfiability"].append(satisfiability)
                        solvability_dict[solver_variation + "_" + "solving_time"].append(solving_time)

                    else:  # no solvability file
                        solvability_dict[solver_variation + "_satisfiability"].append("miss info")
                        solvability_dict[solver_variation + "_solving_time"].append(benchmark_timeout)

    # add virtual best columns
    comparison_solver_list = []
    for k in solver_variation_folders_dict:
        if "pruning" in k or "prioritizing" in k:
            comparison_solver_list.append("vb_" + k)
        else:
            comparison_solver_list.append(k)
    vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
        solvability_dict, comparison_solver_list)
    solvability_dict["vb_satisfiability"] = vb_satisfiability
    solvability_dict["vb_solving_time"] = vb_solving_time

    # add virtual best columns for eldarica
    eldarica_variant_list = [s for s in comparison_solver_list if s not in ["z3", "golem"]]
    vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
        solvability_dict, eldarica_variant_list)
    solvability_dict["vb_eldarica_satisfiability"] = vb_satisfiability
    solvability_dict["vb_eldarica_solving_time"] = vb_solving_time

    # add virtual best columns for original eldarica
    eldarica_variant_list = [s for s in comparison_solver_list if
                             s not in ["z3", "golem"] and "prioritizing" not in s and "pruning" not in s]
    vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
        solvability_dict, eldarica_variant_list)
    solvability_dict["vb_eldarica_original_satisfiability"] = vb_satisfiability
    solvability_dict["vb_eldarica_original_solving_time"] = vb_solving_time
    # add virtual best columns for prioritizing and pruning eldarica in each abstract
    for a in eldarica_abstract_options + ["off"]:
        for strategy in ["prioritizing", "pruning"]:
            eldarica_variant_list = [s for s in comparison_solver_list if
                                     s not in ["z3", "golem"] and strategy in s and a in s]
            vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
                solvability_dict, eldarica_variant_list)
            solvability_dict["vb_eldarica_abstract_" + a + "_" + strategy + "_satisfiability"] = vb_satisfiability
            solvability_dict["vb_eldarica_abstract_" + a + "_" + strategy + "_solving_time"] = vb_solving_time

    # merge symex CDHG and CG and add vb_symex column
    vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
        solvability_dict, ["eldarica_symex_CDHG", "eldarica_symex_CG"])
    solvability_dict["vb_eldarica_symex_prioritize_satisfiability"] = vb_satisfiability
    solvability_dict["vb_eldarica_symex_prioritize_solving_time"] = vb_solving_time
    vb_satisfiability, vb_solving_time = virtual_best_satisfiability_and_solving_time_for_a_solver_list(
        solvability_dict, ["vb_eldarica_symex_prioritize", "eldarica_symex_original"])
    solvability_dict["vb_eldarica_symex_satisfiability"] = vb_satisfiability
    solvability_dict["vb_eldarica_symex_solving_time"] = vb_solving_time

    for k in solvability_dict:
        print(k, len(solvability_dict[k]))

    print("-" * 10)

    return solvability_dict


def virtual_best_satisfiability_and_solving_time_for_a_solver_list(solvability_dict, comparison_solver_list):
    vb_satisfiability = []
    vb_solving_time = []
    for i, f in enumerate(solvability_dict["file_name"]):
        one_file_vb_satisfiability = []
        one_file_vb_solving_time = []
        for k in comparison_solver_list:
            one_file_vb_satisfiability.append(solvability_dict[k + "_satisfiability"][i])
            one_file_vb_solving_time.append(solvability_dict[k + "_solving_time"][i])

        vb_satisfiability.append(virtual_best_satisfiability_from_list(one_file_vb_satisfiability))
        vb_solving_time.append(get_min_number_from_list(one_file_vb_solving_time, -0.001))
    return vb_satisfiability, vb_solving_time


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
    solvability_dict["vb_" + solver_variation + "_" + "satisfiability"].append(satisfiability)
    solvability_dict["vb_" + solver_variation + "_" + "solving_time"].append(solving_time)


def mask_results_by_benchmark_timeout(satisfiability, solving_time):
    if solving_time > benchmark_timeout:
        solving_time = benchmark_timeout
        satisfiability = "unknown"
    return satisfiability, solving_time


def read_pruning_solvability_for_standard_solvers(solvability_dict, full_file_folder, measurements):
    # read pruning solvabilities for z3 and golem
    z3_pruning_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/uppmax-z3-pruning-615/train_data"
    golem_pruning_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/uppmax-golem-pruning-708/train_data"
    for solver, solver_folder in zip(["z3", "golem"], [z3_pruning_folder, golem_pruning_folder]):
        for file in tqdm(get_file_list(full_file_folder, "smt2"), desc="read files"):
            basename = os.path.basename(file)
            current_file = os.path.join(solver_folder, basename)
            if os.path.exists(current_file):
                vb_pruning_satisfiability_list = []
                vb_pruning_solving_time_list = []
                vb_pruning_option_list = []
                for t in threshold_list:
                    for g in ["CDHG", "CG"]:
                        object_list = read_files(
                            [current_file],
                            file_type="pruned-" + g + "-" + str(t) + ".smt2." + solver + "-solvability.JSON",
                            read_function=read_json_file, disable_tqdm=True)
                        for o in object_list:
                            solving_time = read_a_json_field(o, "solving_time")
                            satisfiability = read_a_json_field(o, "satisfiability")
                            vb_pruning_satisfiability_list.append(satisfiability)
                            vb_pruning_solving_time_list.append(solving_time)
                            vb_pruning_option_list.append(g + "-" + str(t))
                vb_satisfiability = "unknown"
                vb_solving_time = benchmark_timeout
                vb_op = "CDHG-0.0"
                for s, st, op in zip(vb_pruning_satisfiability_list, vb_pruning_solving_time_list,
                                     vb_pruning_option_list):
                    if s == "unsafe":
                        vb_satisfiability = s
                        if st < vb_solving_time:
                            vb_solving_time = st
                            vb_op = op

                for m, field in zip(measurements, [vb_satisfiability, str(vb_solving_time) + "[" + vb_op + "]"]):
                    solvability_dict[solver + "_pruning_" + m].append(field)

            else:
                for m in measurements:
                    solvability_dict[solver + "_pruning_" + m].append("miss info")


if __name__ == '__main__':
    main()
