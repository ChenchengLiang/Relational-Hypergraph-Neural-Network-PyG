import os.path

from utils import read_files, read_json_file,get_sumary_folder
from src.utils import get_file_list, make_dirct, select_key_with_value_condition, assign_dict_key_empty_list
import pandas as pd
from src.collect_results.utils import get_min_max_solving_time


def main():
    folder = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_solvability/data"
    summary_folder = get_sumary_folder(folder)
    record_fields = ["file_name", "satisfiability",
                     "min_solving_time_option", "min_solving_time (s)",
                     "min_solving_time_cegar_interation_number",
                     "min_solving_time_generated_predicate_number",
                     "min_solving_time_average_predicate_size", "min_solving_time_predicate_generator_time",
                     "max_solving_time_option", "max_solving_time (s)",
                     "max_solving_time_cegar_interation_number", "max_solving_time_generated_predicate_number",
                     "max_solving_time_average_predicate_size", "max_solving_time_predicate_generator_time"
                     ]
    solvability_dict = {}
    assign_dict_key_empty_list(solvability_dict, record_fields)

    solvability_object_list = read_files(get_file_list(folder, "smt2"), file_type="solvability.JSON",
                                         read_function=read_json_file)
    for object in solvability_object_list:
        if len(object) > 1: # has solvability
            solvability_dict["file_name"].append(os.path.basename(object["file_name"]))

            if int(object["satisfiability-CDHG"][0]) == 0 or int(object["satisfiability-CG"][0]) == 0:
                solvability_dict["satisfiability"].append("unsafe")

                solving_time_dict = {}
                for field in object:
                    if "solvingTime" in field:
                        solving_time_dict[field] = int(object[field][0])
                get_min_max_solving_time(solving_time_dict, solvability_dict, object, min)
                get_min_max_solving_time(solving_time_dict, solvability_dict, object, max)

            else:
                solvability_dict["satisfiability"].append("unknown")
                for field in record_fields:
                    if field not in ["file_name", "satisfiability"]:
                        solvability_dict[field] = 10800
        else: #no solvability file
            solvability_dict["satisfiability"].append("unknown")
            for field in record_fields:
                if field not in ["file_name", "satisfiability"]:
                    solvability_dict[field] = 10800



    # write to excel
    with pd.ExcelWriter(summary_folder + "/solvability_summary.xlsx") as writer:
        data = pd.DataFrame(pd.DataFrame(solvability_dict))
        data.to_excel(writer, sheet_name="solvability")


if __name__ == '__main__':
    main()
