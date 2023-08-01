from src.utils import unzip_file, make_dirct, convert_bytes,select_key_with_value_condition, manual_flatten,float_to_percentage
from src.CONSTANTS import benchmark_timeout
import os
import json
import glob
from shutil import copy
from tqdm import tqdm
import pandas as pd
from src.plots import scatter_plot
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import shutil

import math


def summarize_excel_files():
    excel_files_dict = {
        # "CEGAR-linear-union": ["uppmax-CEGAR-linear-fixed-heuristic-random",
        #                        "uppmax-CEGAR-linear-union-SEHPlus", "uppmax-CEGAR-linear-union-SEHMinus",
        #                        "uppmax-CEGAR-linear-union-REHPlus", "uppmax-CEGAR-linear-union-REHMinus",
        #                        "uppmax-CEGAR-linear-union-mixed-model-SEHPlus",
        #                        "uppmax-CEGAR-linear-union-mixed-model-SEHMinus",
        #                        "uppmax-CEGAR-linear-union-mixed-model-REHPlus",
        #                        "uppmax-CEGAR-linear-union-mixed-model-REHMinus"
        #                        ],
        # "symex-linear-union": ["uppmax-symex-linear-fixed-heuristic-random",
        #                        "uppmax-symex-linear-union-SEHPlus", "uppmax-symex-linear-union-SEHMinus",
        #                        "uppmax-symex-linear-union-REHPlus", "uppmax-symex-linear-union-REHMinus",
        #                        "uppmax-symex-linear-union-linear-model-twoQueue02",
        #                        "uppmax-symex-linear-union-linear-model-twoQueue05",
        #                        "uppmax-symex-linear-union-linear-model-twoQueue08",
        #                        "uppmax-symex-linear-union-mixed-model-SEHPlus",
        #                        "uppmax-symex-linear-union-mixed-model-SEHMinus",
        #                        "uppmax-symex-linear-union-mixed-model-REHPlus",
        #                        "uppmax-symex-linear-union-mixed-model-REHMinus",
        #                        "uppmax-symex-linear-union-mixed-model-REHMinus",
        #                        "uppmax-symex-linear-union-mixed-model-twoQueue02",
        #                        "uppmax-symex-linear-union-mixed-model-twoQueue05",
        #                        "uppmax-symex-linear-union-mixed-model-twoQueue08"
        #                        ],
        # "CEGAR-non-linear-union": ["uppmax-CEGAR-non-linear-fixed-heuristic-random",
        #                            "uppmax-CEGAR-non-linear-union-SEHPlus", "uppmax-CEGAR-non-linear-union-SEHMinus",
        #                            "uppmax-CEGAR-non-linear-union-REHPlus", "uppmax-CEGAR-non-linear-union-REHMinus",
        #                            "uppmax-CEGAR-non-linear-union-mixed-model-SEHPlus",
        #                            "uppmax-CEGAR-non-linear-union-mixed-model-SEHMinus",
        #                            "uppmax-CEGAR-non-linear-union-mixed-model-REHPlus",
        #                            "uppmax-CEGAR-non-linear-union-mixed-model-REHMinus",
        #                            ],
        # "symex-non-linear-union": ["uppmax-symex-non-linear-fixed-heuristic-random",
        #                            "uppmax-symex-non-linear-union-SEHPlus", "uppmax-symex-non-linear-union-SEHMinus",
        #                            "uppmax-symex-non-linear-union-REHPlus", "uppmax-symex-non-linear-union-REHMinus",
        #                            "uppmax-symex-non-linear-union-non-linear-model-twoQueue02",
        #                            "uppmax-symex-non-linear-union-non-linear-model-twoQueue05",
        #                            "uppmax-symex-non-linear-union-non-linear-model-twoQueue08",
        #                            "uppmax-symex-non-linear-union-mixed-model-SEHPlus",
        #                            "uppmax-symex-non-linear-union-mixed-model-SEHMinus",
        #                            "uppmax-symex-non-linear-union-mixed-model-REHPlus",
        #                            "uppmax-symex-non-linear-union-mixed-model-REHMinus",
        #                            "uppmax-symex-non-linear-union-mixed-model-twoQueue02",
        #                            "uppmax-symex-non-linear-union-mixed-model-twoQueue05",
        #                            "uppmax-symex-non-linear-union-mixed-model-twoQueue08"
        #                            ],
        "CEGAR-linear-minimal": ["uppmax-CEGAR-linear-fixed-heuristic-random",
                                 "uppmax-CEGAR-linear-minimal-linear-model-rank",
                                 "uppmax-CEGAR-linear-minimal-linear-model-score",
                                 "uppmax-CEGAR-linear-minimal-linear-model-SEHPlus", "uppmax-CEGAR-linear-minimal-linear-model-SEHMinus",
                                 "uppmax-CEGAR-linear-minimal-linear-model-REHPlus", "uppmax-CEGAR-linear-minimal-linear-model-REHMinus",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-rank",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-score",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-SEHPlus",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-SEHMinus",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-REHPlus",
                                 "uppmax-CEGAR-linear-minimal-mixed-model-REHMinus",
                                 ],
        "symex-linear-minimal": ["uppmax-symex-linear-fixed-heuristic-random",
                                 "uppmax-symex-linear-minimal-linear-model-rank",
                                 "uppmax-symex-linear-minimal-linear-model-score",
                                 "uppmax-symex-linear-minimal-linear-model-SEHPlus", "uppmax-symex-linear-minimal-linear-model-SEHMinus",
                                 "uppmax-symex-linear-minimal-linear-model-REHPlus", "uppmax-symex-linear-minimal-linear-model-REHMinus",
                                 "uppmax-symex-linear-minimal-linear-model-twoQueue02",
                                 "uppmax-symex-linear-minimal-linear-model-twoQueue05",
                                 "uppmax-symex-linear-minimal-linear-model-twoQueue08",
                                 "uppmax-symex-linear-minimal-linear-model-schedule10",
                                 "uppmax-symex-linear-minimal-linear-model-schedule100",
                                 "uppmax-symex-linear-minimal-linear-model-schedule1000",
                                 "uppmax-symex-linear-minimal-mixed-model-rank",
                                 "uppmax-symex-linear-minimal-mixed-model-score",
                                 "uppmax-symex-linear-minimal-mixed-model-SEHPlus",
                                 "uppmax-symex-linear-minimal-mixed-model-SEHMinus",
                                 "uppmax-symex-linear-minimal-mixed-model-REHPlus",
                                 "uppmax-symex-linear-minimal-mixed-model-REHMinus",
                                 "uppmax-symex-linear-minimal-mixed-model-twoQueue02",
                                 "uppmax-symex-linear-minimal-mixed-model-twoQueue05",
                                 "uppmax-symex-linear-minimal-mixed-model-twoQueue08",
                                 "uppmax-symex-linear-minimal-mixed-model-schedule10",
                                 "uppmax-symex-linear-minimal-mixed-model-schedule100",
                                 "uppmax-symex-linear-minimal-mixed-model-schedule1000"
                                 ],
        "CEGAR-non-linear-minimal": ["uppmax-CEGAR-non-linear-fixed-heuristic-random",
                                     "uppmax-CEGAR-non-linear-minimal-non-linear-model-rank",
                                     "uppmax-CEGAR-non-linear-minimal-non-linear-model-score",
                                     "uppmax-CEGAR-non-linear-minimal-non-linear-model-SEHPlus", "uppmax-CEGAR-non-linear-minimal-non-linear-model-SEHMinus",
                                     "uppmax-CEGAR-non-linear-minimal-non-linear-model-REHPlus", "uppmax-CEGAR-non-linear-minimal-non-linear-model-REHMinus",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-rank",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-score",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-SEHPlus",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-SEHMinus",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-REHPlus",
                                     "uppmax-CEGAR-non-linear-minimal-mixed-model-REHMinus",
                                     ],
        "symex-non-linear-minimal": ["uppmax-symex-non-linear-fixed-heuristic-random",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-rank",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-score",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-SEHPlus", "uppmax-symex-non-linear-minimal-non-linear-model-SEHMinus",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-REHPlus", "uppmax-symex-non-linear-minimal-non-linear-model-REHMinus",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-twoQueue02",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-twoQueue05",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-twoQueue08",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-schedule10",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-schedule100",
                                     "uppmax-symex-non-linear-minimal-non-linear-model-schedule1000",
                                     "uppmax-symex-non-linear-minimal-mixed-model-rank",
                                     "uppmax-symex-non-linear-minimal-mixed-model-score",
                                     "uppmax-symex-non-linear-minimal-mixed-model-SEHPlus",
                                     "uppmax-symex-non-linear-minimal-mixed-model-SEHMinus",
                                     "uppmax-symex-non-linear-minimal-mixed-model-REHPlus",
                                     "uppmax-symex-non-linear-minimal-mixed-model-REHMinus",
                                     "uppmax-symex-non-linear-minimal-mixed-model-twoQueue02",
                                     "uppmax-symex-non-linear-minimal-mixed-model-twoQueue05",
                                     "uppmax-symex-non-linear-minimal-mixed-model-twoQueue08",
                                     "uppmax-symex-non-linear-minimal-mixed-model-schedule10",
                                     "uppmax-symex-non-linear-minimal-mixed-model-schedule100",
                                     "uppmax-symex-non-linear-minimal-mixed-model-schedule1000"
                                     ],

        "CEGAR-linear-common": ["uppmax-CEGAR-linear-fixed-heuristic-random",
                                "uppmax-CEGAR-linear-common-linear-model-rank",
                                "uppmax-CEGAR-linear-common-linear-model-score",
                                 "uppmax-CEGAR-linear-common-linear-model-SEHPlus",
                                 "uppmax-CEGAR-linear-common-linear-model-SEHMinus",
                                 "uppmax-CEGAR-linear-common-linear-model-REHPlus",
                                 "uppmax-CEGAR-linear-common-linear-model-REHMinus",
                                 "uppmax-CEGAR-linear-common-mixed-model-rank",
                                 "uppmax-CEGAR-linear-common-mixed-model-score",
                                 "uppmax-CEGAR-linear-common-mixed-model-SEHPlus",
                                 "uppmax-CEGAR-linear-common-mixed-model-SEHMinus",
                                 "uppmax-CEGAR-linear-common-mixed-model-REHPlus",
                                 "uppmax-CEGAR-linear-common-mixed-model-REHMinus",
                                 ],
        "symex-linear-common": ["uppmax-symex-linear-fixed-heuristic-random",
                                "uppmax-symex-linear-common-linear-model-rank",
                                "uppmax-symex-linear-common-linear-model-score",
                                 "uppmax-symex-linear-common-linear-model-SEHPlus",
                                 "uppmax-symex-linear-common-linear-model-SEHMinus",
                                 "uppmax-symex-linear-common-linear-model-REHPlus",
                                 "uppmax-symex-linear-common-linear-model-REHMinus",
                                "uppmax-symex-linear-common-linear-model-schedule10",
                                "uppmax-symex-linear-common-linear-model-schedule100",
                                "uppmax-symex-linear-common-linear-model-schedule1000",
                                 "uppmax-symex-linear-common-mixed-model-rank",
                                 "uppmax-symex-linear-common-mixed-model-score",
                                 "uppmax-symex-linear-common-mixed-model-SEHPlus",
                                 "uppmax-symex-linear-common-mixed-model-SEHMinus",
                                 "uppmax-symex-linear-common-mixed-model-REHPlus",
                                 "uppmax-symex-linear-common-mixed-model-REHMinus",
                                 "uppmax-symex-linear-common-mixed-model-twoQueue02",
                                 "uppmax-symex-linear-common-mixed-model-twoQueue05",
                                 "uppmax-symex-linear-common-mixed-model-twoQueue08",
                                "uppmax-symex-linear-common-mixed-model-schedule10",
                                "uppmax-symex-linear-common-mixed-model-schedule100",
                                "uppmax-symex-linear-common-mixed-model-schedule1000"
                                 ],
        "CEGAR-non-linear-common": ["uppmax-CEGAR-non-linear-fixed-heuristic-random",
                                    "uppmax-CEGAR-non-linear-common-non-linear-model-rank",
                                    "uppmax-CEGAR-non-linear-common-non-linear-model-score",
                                     "uppmax-CEGAR-non-linear-common-non-linear-model-SEHPlus",
                                     "uppmax-CEGAR-non-linear-common-non-linear-model-SEHMinus",
                                     "uppmax-CEGAR-non-linear-common-non-linear-model-REHPlus",
                                     "uppmax-CEGAR-non-linear-common-non-linear-model-REHMinus",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-rank",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-score",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-SEHPlus",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-SEHMinus",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-REHPlus",
                                     "uppmax-CEGAR-non-linear-common-mixed-model-REHMinus",
                                     ],
        "symex-non-linear-common": ["uppmax-symex-non-linear-fixed-heuristic-random",
                                    "uppmax-symex-non-linear-common-non-linear-model-rank",
                                    "uppmax-symex-non-linear-common-non-linear-model-score",
                                     "uppmax-symex-non-linear-common-non-linear-model-SEHPlus",
                                     "uppmax-symex-non-linear-common-non-linear-model-SEHMinus",
                                     "uppmax-symex-non-linear-common-non-linear-model-REHPlus",
                                     "uppmax-symex-non-linear-common-non-linear-model-REHMinus",
                                     "uppmax-symex-non-linear-common-non-linear-model-twoQueue02",
                                     "uppmax-symex-non-linear-common-non-linear-model-twoQueue05",
                                     "uppmax-symex-non-linear-common-non-linear-model-twoQueue08",
                                    "uppmax-symex-non-linear-common-non-linear-model-schedule10",
                                    "uppmax-symex-non-linear-common-non-linear-model-schedule100",
                                    "uppmax-symex-non-linear-common-non-linear-model-schedule1000",
                                     "uppmax-symex-non-linear-common-mixed-model-rank",
                                     "uppmax-symex-non-linear-common-mixed-model-score",
                                     "uppmax-symex-non-linear-common-mixed-model-SEHPlus",
                                     "uppmax-symex-non-linear-common-mixed-model-SEHMinus",
                                     "uppmax-symex-non-linear-common-mixed-model-REHPlus",
                                     "uppmax-symex-non-linear-common-mixed-model-REHMinus",
                                     "uppmax-symex-non-linear-common-mixed-model-twoQueue02",
                                     "uppmax-symex-non-linear-common-mixed-model-twoQueue05",
                                     "uppmax-symex-non-linear-common-mixed-model-twoQueue08",
                                     "uppmax-symex-non-linear-common-mixed-model-schedule10",
                                     "uppmax-symex-non-linear-common-mixed-model-schedule100",
                                     "uppmax-symex-non-linear-common-mixed-model-schedule1000"
                                     ],

        # "CEGAR-linear-train+valid-union": ["uppmax-CEGAR-linear-train+valid-union-random-869",
        #                                    "uppmax-CEGAR-linear-train+valid-union-label-869"],
        # "symex-linear-train+valid-union": ["uppmax-symex-linear-train+valid-union-random-869",
        #                                    "uppmax-symex-linear-train+valid-union-label-869"],
        # "CEGAR-linear-train+valid-minimal": ["uppmax-CEGAR-linear-train+valid-minimal-random-861",
        #                                      "uppmax-CEGAR-linear-train+valid-minimal-label-861"],
        # "symex-linear-train+valid-minimal": ["uppmax-symex-linear-train+valid-minimal-random-861",
        #                                      "uppmax-symex-linear-train+valid-minimal-label-861"],
        # "CEGAR-non-linear-train+valid-union": ["uppmax-CEGAR-non-linear-train+valid-union-label-1797",
        #                                        "uppmax-CEGAR-non-linear-train+valid-union-random-1797"],
        # "symex-non-linear-train+valid-union": ["uppmax-symex-non-linear-train+valid-union-random-1797",
        #                                        "uppmax-symex-non-linear-train+valid-union-label-1797"],
    }

    # non-linear
    # excel_files = ["uppmax-CEGAR-non-linear-train+valid-union-label-1797"]# CEGAR train+valid
    # excel_files = ["uppmax-synex-non-linear-train+valid-union-random-1797","uppmax-symex-non-linear-train+valid-union-label-1797"]  # symex train+valid

    summary_file = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/summary.xlsx"
    # write summary excel
    with pd.ExcelWriter(summary_file) as writer:
        for k in excel_files_dict:
            excel_files = excel_files_dict[k]
            columns = ["category"] + ["total","original_solved","original_safe", "original_unsafe", "original_avg_t","original_avg_t_s","original_avg_t_cs","original_avg_t_ocs","original_avg_t_safe","original_avg_t_unsafe"] + manual_flatten(
                [[f + "_solved",f + "_safe", f + "_unsafe", f + "_avg_t",f + "_avg_t_s",f + "_avg_t_cs",f+"_avg_t_ocs",f+"_avg_t_safe",f+"_avg_t_unsafe"] for f in excel_files])
            output_dict = {x: [] for x in columns}
            engine = "symex" if "symex" in excel_files[0] else "CEGAR"

            # get original safe and unsafe
            solvability_dict = read_solvability_dict(
                "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/" +
                excel_files[0] + ".xlsx",
                sheet_name="category_summary")

            output_dict["total"] = ["total"] + solvability_dict["number_predicted"]

            output_dict["original_solved"] = ["solved"] + [a + b for a, b in
                                                         zip(solvability_dict["eldarica_" + engine + "_original_safe"],
                                                             solvability_dict[
                                                                 "eldarica_" + engine + "_original_unsafe"])]
            output_dict["original_safe"] = ["safe"] + solvability_dict["eldarica_" + engine + "_original_safe"]
            output_dict["original_unsafe"] = ["unsafe"] + solvability_dict["eldarica_" + engine + "_original_unsafe"]
            solving_time_list=solvability_dict["eldarica_" + engine + "_original_solving_time"]
            common_solving_time_list = solvability_dict["eldarica_" + engine + "_original_common_solving_time"]
            common_original_solving_time_list = solvability_dict["eldarica_" + engine + "_original_common_original_solving_time"]
            common_solving_count_list = solvability_dict["eldarica_" + engine + "_original_common_solving_count"]
            sat_solving_time_list=solvability_dict["eldarica_" + engine + "_original_sat_solving_time"]
            sat_solving_count_list=solvability_dict["eldarica_" + engine + "_original_safe"]
            unsat_solving_time_list=solvability_dict["eldarica_" + engine + "_original_unsat_solving_time"]
            unsat_solving_count_list=solvability_dict["eldarica_" + engine + "_original_unsafe"]
            average_solving_time_list,average_solving_time_solved_list,average_solving_common_solving_time_list,average_solving_common_original_solving_time_list,average_safe_solving_time_list,average_unsafe_solving_time_list = compute_average_solving_time(
                output_dict["total"],output_dict["original_solved"] ,solving_time_list,common_solving_time_list,common_solving_count_list,common_original_solving_time_list,sat_solving_time_list,sat_solving_count_list,unsat_solving_time_list,unsat_solving_count_list)
            output_dict["original_avg_t"] = ["avg_t"] + [x if isinstance(x,str) else format(x,".2f") for x in average_solving_time_list]
            output_dict["original_avg_t_s"] = ["avg_t_s"] + [x if isinstance(x,str) else format(x,".2f") for x in average_solving_time_solved_list]
            output_dict["original_avg_t_cs"] = ["avg_t_cs"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_solving_common_solving_time_list]
            output_dict["original_avg_t_ocs"] = ["avg_t_ocs"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_solving_common_original_solving_time_list]
            output_dict["original_avg_t_safe"] = ["avg_t_safe"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_safe_solving_time_list]
            output_dict["original_avg_t_unsafe"] = ["avg_t_unsafe"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_unsafe_solving_time_list]
            output_dict["category"] = [" "] + solvability_dict["category"]


            # get safe and unsafe from other excels
            for f in excel_files:
                solvability_dict = read_solvability_dict(
                    "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/" + f + ".xlsx",
                    sheet_name="category_summary")
                output_dict[f + "_solved"] = ["solved"] + [a + b for a, b in zip(
                    solvability_dict["vb_eldarica_" + engine + "_prioritize_safe"],
                    solvability_dict["vb_eldarica_" + engine + "_prioritize_unsafe"])]
                output_dict[f + "_safe"] = ["safe"] + solvability_dict["vb_eldarica_" + engine + "_prioritize_safe"]
                output_dict[f + "_unsafe"] = ["unsafe"] + solvability_dict[
                    "vb_eldarica_" + engine + "_prioritize_unsafe"]
                solving_time_list=solvability_dict["vb_eldarica_" + engine + "_prioritize_solving_time"]
                common_solving_time_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_common_solving_time"]
                common_original_solving_time_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_common_original_solving_time"]
                common_solving_count_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_common_solving_count"]
                sat_solving_time_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_sat_solving_time"]
                sat_solving_count_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_safe"]
                unsat_solving_time_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_unsat_solving_time"]
                unsat_solving_count_list = solvability_dict["vb_eldarica_" + engine + "_prioritize_unsafe"]
                average_solving_time_list,average_solving_time_solved_list,average_solving_common_solving_time_list,average_solving_common_original_solving_time_list,average_safe_solving_time_list,average_unsafe_solving_time_list = compute_average_solving_time(output_dict["total"],output_dict[f + "_solved"]
                ,solving_time_list,common_solving_time_list,common_solving_count_list,common_original_solving_time_list,sat_solving_time_list,sat_solving_count_list,unsat_solving_time_list,unsat_solving_count_list)
                output_dict[f + "_avg_t"] = ["avg_t"] + [x if isinstance(x,str) else format(x,".2f") for x in average_solving_time_list]
                output_dict[f + "_avg_t_s"] = ["avg_t_s"] + [x if isinstance(x,str) else format(x,".2f") for x in average_solving_time_solved_list]
                output_dict[f + "_avg_t_cs"] = ["avg_t_cs"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_solving_common_solving_time_list]
                output_dict[f + "_avg_t_ocs"] = ["avg_t_ocs"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_solving_common_original_solving_time_list]
                output_dict[f + "_avg_t_safe"] = ["avg_t_safe"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_safe_solving_time_list]
                output_dict[f + "_avg_t_unsafe"] = ["avg_t_unsafe"] + [x if isinstance(x, str) else format(x, ".2f") for x in average_unsafe_solving_time_list]

            # for x in output_dict:
            #     print(x,len(output_dict[x]))
            pd.DataFrame(pd.DataFrame(output_dict)).to_excel(writer, sheet_name=k)

            #get common solved time


    # merge some cells
    for e_k in excel_files_dict:
        excel_files = excel_files_dict[e_k]
        # Load the Excel file
        workbook = load_workbook(summary_file)
        # Select the desired sheet
        sheet = workbook[e_k]

        # Merge cells
        sheet.merge_cells('D1:L1')  # Merge cells in the range
        sheet["D1"].value = "Original"

        merge_dict = {f: [] for f in excel_files}
        last_column_letter = sheet.dimensions.split(':')[1].strip('1234567890')
        for f in excel_files:
            for row in sheet["E1:" + last_column_letter + "1"]:
                for cell in row:
                    if (f + "_solved" == cell.value or f + "_safe" == cell.value or f + "_unsafe" == cell.value or f + "_avg_t" == cell.value or
                            f + "_avg_t_s" == cell.value or f + "_avg_t_cs" == cell.value or f + "_avg_t_ocs" == cell.value or f + "_avg_t_safe" == cell.value or f + "_avg_t_unsafe" == cell.value):
                        merge_dict[f].append(cell.coordinate)
        for k in merge_dict:
            sheet.merge_cells(merge_dict[k][0] + ":" + merge_dict[k][-1])
            sheet[merge_dict[k][0]].value = k.replace(e_k + "-", "").replace("uppmax-", "")

        # add scatter plot inside
        count = 18 #row number
        for f in excel_files:
            img = Image(
                "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/" + f + ".png")
            sheet["A" + str(count)] = ''
            sheet["A" + str(count)].comment = None
            sheet.add_image(img, 'A' + str(count))
            count += 35 #row number

        #compute improve percentage for solving time
        row =13 if "non-linear" in e_k else 15
        column_number = 9
        sheet["B" + str(row + 2)].value = "improve percentage"

        oirginal_column_number = 4  # solved
        compute_improved_percentage(sheet, oirginal_column_number, row, column_number)
        oirginal_column_number = 5  # safe
        compute_improved_percentage(sheet, oirginal_column_number, row, column_number)
        oirginal_column_number = 6  # unsafe
        compute_improved_percentage(sheet, oirginal_column_number, row, column_number)
        oirginal_st_column_number=7 #avg_t
        compute_improved_percentage_solving_time(sheet, oirginal_st_column_number, row, column_number)
        oirginal_st_column_number=8 #avg_t_s
        compute_improved_percentage_solving_time(sheet, oirginal_st_column_number, row, column_number)
        oirginal_st_column_number=9 #avg_t_cs
        compute_improved_percentage_for_common_solving_time(sheet, oirginal_st_column_number, row, column_number)
        oirginal_st_column_number = 11  # avg_t_safe
        compute_improved_percentage_solving_time(sheet, oirginal_st_column_number, row, column_number)
        oirginal_st_column_number = 12  # avg_t_unsafe
        compute_improved_percentage_solving_time(sheet, oirginal_st_column_number, row, column_number)

        # Save the modified workbook
        workbook.save(summary_file)

def compute_improved_percentage_for_common_solving_time(sheet,oirginal_st_column_number,row,column_number):
    current_st_column_number=oirginal_st_column_number
    while sheet[get_column_letter(current_st_column_number) + str(row)].value is not None:
        target_st_value = float(sheet[get_column_letter(current_st_column_number) + str(row)].value) # avg_t_cs
        oirginal_st_value = float(sheet[get_column_letter(current_st_column_number + 1) + str(row)].value)  # avg_t_ocs
        improve_percentage = (oirginal_st_value - target_st_value) / oirginal_st_value
        sheet[get_column_letter(current_st_column_number) + str(row + 2)].value = float_to_percentage(improve_percentage)
        current_st_column_number = current_st_column_number + column_number
def compute_improved_percentage_solving_time(sheet,oirginal_st_column_number,row,column_number):
    oirginal_st_value = float(sheet[get_column_letter(oirginal_st_column_number) + str(row)].value)
    current_st_column_number = oirginal_st_column_number + column_number
    while sheet[get_column_letter(current_st_column_number) + str(row)].value is not None:
        target_st_value = float(sheet[get_column_letter(current_st_column_number) + str(row)].value)
        improve_percentage = (oirginal_st_value - target_st_value) / oirginal_st_value
        sheet[get_column_letter(current_st_column_number) + str(row + 2)].value = float_to_percentage(
            improve_percentage)
        current_st_column_number = current_st_column_number + column_number
def compute_improved_percentage(sheet,oirginal_column_number,row,column_number):
    oirginal_st_value = float(sheet[get_column_letter(oirginal_column_number) + str(row)].value)
    current_st_column_number = oirginal_column_number + column_number
    while sheet[get_column_letter(current_st_column_number) + str(row)].value is not None:
        target_st_value = float(sheet[get_column_letter(current_st_column_number) + str(row)].value)
        improve_percentage = (target_st_value-oirginal_st_value) / oirginal_st_value
        sheet[get_column_letter(current_st_column_number) + str(row + 2)].value = float_to_percentage(
            improve_percentage)
        current_st_column_number = current_st_column_number + column_number

def get_column_letter(col_num):
    letter = ''
    while col_num:
        col_num, remainder = divmod(col_num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter

def compute_average_solving_time(list_total, list_solved, list_time,list_common_time,common_solving_count,list_common_original_time,sat_solving_time_list,sat_solving_count_list,unsat_solving_time_list,unsat_solving_count_list):
    average_solving_time_list=[]
    average_solving_time_solved_list = []
    average_common_solving_time_list = []
    average_common_original_solving_time_list=[]
    average_safe_solving_time_list=[]
    average_unsafe_solving_time_list=[]
    #compute average solving time
    for x, y in zip(list_total[1:], list_time):
        if isinstance(x, str):
            average_solving_time_list.append(x)
        elif x == 0:
            average_solving_time_list.append(0)
        else:
            average_solving_time_list.append(y / x)
    #compute average solving time for safe
    for x, y, z in zip(list_total[1:], sat_solving_time_list, sat_solving_count_list):
        if isinstance(x, str):
            average_safe_solving_time_list.append(x)
        elif z == 0:
            average_safe_solving_time_list.append(0)
        else:
            average_safe_solving_time_list.append(y / z)
    #compute average solving time for unsafe
    for x, y, z in zip(list_total[1:], unsat_solving_time_list, unsat_solving_count_list):
        if isinstance(x, str):
            average_unsafe_solving_time_list.append(x)
        elif z == 0:
            average_unsafe_solving_time_list.append(0)
        else:
            average_unsafe_solving_time_list.append(y / z)
    #compute average solving time for solved
    for t,s,time in zip(list_total[1:],list_solved[1:], list_time):
        if isinstance(t, str):
            average_solving_time_solved_list.append(t)
        elif s==0:
            average_solving_time_solved_list.append(0)
        else:
            numerator = (time - (t - s) * benchmark_timeout)
            average_solving_time_solved_list.append(numerator/ s)
    #compute average solving time for common solved
    for x, y, z in zip(list_total[1:], list_common_time,common_solving_count):
        if isinstance(x, str):
            average_common_solving_time_list.append(x)
        elif z == 0:
            average_common_solving_time_list.append(0)
        else:
            average_common_solving_time_list.append(y / z)
    # compute average solving time for original common solved
    for x, y, z in zip(list_total[1:], list_common_original_time, common_solving_count):
        if isinstance(x, str):
            average_common_original_solving_time_list.append(x)
        elif z == 0:
            average_common_original_solving_time_list.append(0)
        else:
            average_common_original_solving_time_list.append(y / z)


    return average_solving_time_list,average_solving_time_solved_list,average_common_solving_time_list,average_common_original_solving_time_list,average_safe_solving_time_list,average_unsafe_solving_time_list
def draw_solving_time_scatter(excel_file, compare_benchmark_name):
    # Read the Excel file into a Pandas DataFrame
    solvability_dict = read_solvability_dict(excel_file)
    plot_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/scatter_plots"
    shutil.rmtree(plot_folder)
    scatter_folder = make_dirct(plot_folder)

    if "eldarica_symex_original_satisfiability" in solvability_dict.keys():
        apptainer_data_pair = ["eldarica_symex_original", "vb_eldarica_symex_prioritize"]
    elif "eldarica_CEGAR_original_satisfiability" in solvability_dict.keys():
        apptainer_data_pair = ["eldarica_CEGAR_original", "vb_eldarica_CEGAR_prioritize"]

    comparison_pairs = [["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_SEH"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_score"],
                        # ["eldarica_symex_original", "vb_eldarica_symex_prioritize"],
                        # ["eldarica_symex_original", "pf_eldarica_symex"]
                        # ["eldarica_CEGAR_original", "vb_eldarica_CEGAR_prioritize"],
                        ] + [apptainer_data_pair]

    axis_name_map = {"eldarica_abstract_off": "Original",
                     "vb_eldarica_abstract_off_prioritizing_SEH": "prioritizing score+",
                     "vb_eldarica_abstract_off_prioritizing_rank": "Prioritizing score",
                     "vb_eldarica_abstract_off_pruning_rank": "Pruning rank",
                     "vb_eldarica_abstract_off_pruning_score": "Pruning score",
                     "eldarica_symex_original": "Original", "vb_eldarica_symex_prioritize": "Prioritizing_score",
                     "eldarica_CEGAR_original": "Original", "vb_eldarica_CEGAR_prioritize": "Prioritizing_score"
                     }
    for pair in comparison_pairs:
        if "symex" in pair[0]:
            engine = "Symex"
        else:
            engine = "CEGAR"
        # draw common solvig time scatter
        original_solving_time_list_common = []
        strategy_solving_time_list_common = []
        satisfiability_list_common = []
        file_name_list_common = []
        # draw all solvig time scatter
        original_solving_time_list_all = []
        strategy_solving_time_list_all = []
        satisfiability_list_all = []
        file_name_list_all = []

        for name, original_s, strategy_s, original_st, strategy_st in zip(solvability_dict["file_name"],
                                                                          solvability_dict[pair[0] + "_satisfiability"],
                                                                          solvability_dict[pair[1] + "_satisfiability"],
                                                                          solvability_dict[pair[0] + "_solving_time"],
                                                                          solvability_dict[pair[1] + "_solving_time"]):
            vb_satisfiability = virtual_best_satisfiability_from_list([original_s, strategy_s])
            # file_name_list_all.append(name)
            # satisfiability_list_all.append(vb_satisfiability)
            # original_solving_time_list_all.append(original_st)
            # strategy_solving_time_list_all.append(strategy_st)
            # collect all solvable solving time and solvability
            if vb_satisfiability != "unknown":
                file_name_list_all.append(name)
                satisfiability_list_all.append(vb_satisfiability)
                original_solving_time_list_all.append(original_st)
                strategy_solving_time_list_all.append(strategy_st)
                # collect common solvable solving time and solvability
                if original_s == strategy_s:
                    file_name_list_common.append(name)
                    satisfiability_list_common.append(vb_satisfiability)
                    original_solving_time_list_common.append(original_st)
                    strategy_solving_time_list_common.append(strategy_st)

        scatter_plot(x_data=original_solving_time_list_common, y_data=strategy_solving_time_list_common,
                     z_data=satisfiability_list_common,
                     x_axis=axis_name_map[pair[0]], y_axis=axis_name_map[pair[1]], folder=scatter_folder,
                     data_text=file_name_list_common,
                     name="Common-solving-time" + "<br>" + compare_benchmark_name, scale="log")
        scatter_plot(x_data=original_solving_time_list_all, y_data=strategy_solving_time_list_all,
                     z_data=satisfiability_list_all,
                     x_axis=axis_name_map[pair[0]], y_axis=axis_name_map[pair[1]], folder=scatter_folder,
                     data_text=file_name_list_all,
                     name="All-solving-time" + "<br>" + compare_benchmark_name, scale="log")


def read_solvability_dict(excel_file, sheet_name="data"):
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)

    # Convert the DataFrame to a dictionary
    solvability_dict = df.to_dict(orient='list')
    return solvability_dict


def read_json_file(file, json_obj):
    try:
        loaded_graph = json.load(file)
    except ValueError as e:
        file = file.name
        print("json.load() error", file)
        file_name = file[:file.find("smt2") + 4]
        copy_relative_files(file_name,
                            "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics-debug")
        return json_obj
    for field in loaded_graph:
        # print(bcolors.GRENN + str(field) + str(loaded_graph[field]) + bcolors.RESET)
        json_obj[str(field)] = loaded_graph[field]
    return json_obj


def read_graph_generation_log(f, json_obj):
    for l in f.readlines():
        for g in ["CDHG", "CG"]:
            if g in l:
                json_obj.update({g + "_time_consumption": int(l[l.find(":") + 1:l.find("milliseconds")])})
    return json_obj


def read_smt2_category(f, json_obj):
    first_line = f.readline()[1:]
    json_obj["category"] = os.path.dirname(first_line)
    return json_obj


def read_files(file_list, file_type="solvability.JSON", read_function=read_json_file, disable_tqdm=False):
    '''notice: this is a generator and the returned interator can only be used once'''
    for file in tqdm(file_list, desc="read " + file_type, disable=disable_tqdm):
        file_name = file[:-len(".zip")]
        json_file = file_name + "." + file_type if len(file_type) != 0 else file_name
        try:
            unzip_file(json_file + ".zip")
        except:
            exception_folder = make_dirct(os.path.dirname(os.path.dirname(file)) + "/unzip_exceptions")
            copy_relative_files(file_name, exception_folder)
        json_obj = {}
        json_obj["file_name"] = json_file[:-len(file_type) - 1]
        if os.path.exists(json_file):
            json_obj["file_size"] = os.path.getsize(json_file)
            json_obj["file_size_h"] = convert_bytes(os.path.getsize(json_file))
            with open(json_file) as f:
                read_function(f, json_obj)
                # delete unziped file
            if os.path.exists(json_file + ".zip"):
                os.remove(json_file)
            yield json_obj
        else:
            yield json_obj


def get_sumary_folder(folder):
    summary_folder = os.path.dirname(folder) + "/" + os.path.basename(folder) + "_summary"
    make_dirct(summary_folder)
    return summary_folder


def copy_relative_files(file_name, folder):
    for f in glob.glob(file_name + "*"):
        copy(f, folder)


def get_min_max_solving_time(solving_time_dict, data_dict, object, func=min):
    solving_option, solving_time = select_key_with_value_condition(solving_time_dict, func)
    solving_time_cegar_interation_number = int(
        float(object[solving_option.replace("solvingTime", "cegarIterationNumber")][0]))
    solving_time_generated_predicate_number = int(
        float(object[solving_option.replace("solvingTime", "generatedPredicateNumber")][0]))
    solving_time_average_predicate_size = int(
        float(object[solving_option.replace("solvingTime", "averagePredicateSize")][0]))
    solving_time_predicate_generator_time = int(
        float(object[solving_option.replace("solvingTime", "predicateGeneratorTime")][0]))

    data_dict[func.__name__ + "_solving_time_option"].append(solving_option.replace("solvingTime_", ""))
    data_dict[func.__name__ + "_solving_time (s)"].append(solving_time / 1000)
    data_dict[func.__name__ + "_solving_time_cegar_interation_number"].append(
        solving_time_cegar_interation_number)
    data_dict[func.__name__ + "_solving_time_generated_predicate_number"].append(
        solving_time_generated_predicate_number)
    data_dict[func.__name__ + "_solving_time_average_predicate_size"].append(
        solving_time_average_predicate_size)
    data_dict[func.__name__ + "_solving_time_predicate_generator_time"].append(
        solving_time_predicate_generator_time)
    return solving_option, solving_time / 1000


def get_solving_time_dict(object):
    solving_time_dict = {}
    for field in object:
        if "solvingTime" in field:
            solving_time_dict[field] = int(float(object[field][0]))
            if solving_time_dict[field] == -1:
                solving_time_dict[field] = 10800000
    return solving_time_dict


def virtual_best_satisfiability_from_list(s):
    if "safe" in s and "unsafe" in s:
        return "unsound error"
    elif "safe" in s:
        return "safe"
    elif "unsafe" in s:
        return "unsafe"
    elif all(element == "miss info" for element in s):
        return "miss info"
    else:
        return "unknown"
