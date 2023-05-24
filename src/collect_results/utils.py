from src.utils import unzip_file, make_dirct, convert_bytes
import os
import json
import glob
from shutil import copy
from tqdm import tqdm
from src.utils import select_key_with_value_condition,manual_flatten
import pandas as pd
from src.plots import scatter_plot
from openpyxl import load_workbook

def summarize_excel_files():
    excel_files = ["symex-birthTime","symex-new-birthTime","symex-constraintSum","symex-score+constrainSum",
                   "symex-only-score-100","symex-only-score-1000","symex-only-score-10000",
                   "symex-socre+birthTime","symex-score+new-birthTime","symex-score+birthTime+constrainSum",
                   "symex-rank","symex-rank-inverse","symex-rank+birthTime","symex-rank+new-birthTime",
                   "symex-rank+new-birthTime-inverse",
                   "symex-rank+birthTime+constraintSum",]
    columns = ["category"]+["original_safe","original_unsafe"]+manual_flatten([[f + "_safe", f + "_unsafe"] for f in excel_files])
    output_dict = {x: [] for x in columns}

    #get original safe and unsafe
    solvability_dict = read_solvability_dict(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/symex-new-birthTime.xlsx",
        sheet_name="category_summary")
    output_dict["original_safe"] = ["safe"]+solvability_dict["eldarica_symex_original_safe"]
    output_dict["original_unsafe"] = ["unsafe"]+solvability_dict["eldarica_symex_original_unsafe"]
    output_dict["category"]=[" "]+solvability_dict["category"]

    #get safe and unsafe from other excels
    for f in excel_files:
        solvability_dict = read_solvability_dict(
            "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/" + f + ".xlsx",
            sheet_name="category_summary")
        output_dict[f + "_safe"] = ["safe"]+solvability_dict["vb_eldarica_symex_prioritize_safe"]
        output_dict[f + "_unsafe"] = ["unsafe"]+solvability_dict["vb_eldarica_symex_prioritize_unsafe"]

    summary_file="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/summary.xlsx"
    #write summary excel
    with pd.ExcelWriter(summary_file) as writer:
        pd.DataFrame(pd.DataFrame(output_dict)).to_excel(writer, sheet_name="summary")

    #merge some cells
    # Load the Excel file
    workbook = load_workbook(summary_file)
    # Select the desired sheet
    sheet = workbook['summary']

    # Merge cells
    sheet.merge_cells('C1:D1')  # Merge cells in the range C1 to D1
    sheet["C1"].value="Original"

    merge_dict={f:[] for f in excel_files}
    last_column_letter = sheet.dimensions.split(':')[1].strip('1234567890')
    for f in excel_files:
        for row in sheet["E1:"+last_column_letter+"1"]:
            for cell in row:
                if f+"_safe" == cell.value or f+"_unsafe" == cell.value:
                    merge_dict[f].append(cell.coordinate)
    for k in merge_dict:
        sheet.merge_cells(merge_dict[k][0]+":"+merge_dict[k][-1])
        sheet[merge_dict[k][0]].value=k

    # Save the modified workbook
    workbook.save(summary_file)


def draw_common_unsafe_solving_time(excel_file):
    # Read the Excel file into a Pandas DataFrame
    solvability_dict = read_solvability_dict(excel_file)
    scatter_folder = make_dirct(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/scatter_plots")

    comparison_pairs = [["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_SEH"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_score"],
                        ["eldarica_symex_original", "vb_eldarica_symex_prioritize"],
                        # ["eldarica_symex_original", "pf_eldarica_symex"]
                        ]

    axis_name_map = {"eldarica_abstract_off": "Original",
                     "vb_eldarica_abstract_off_prioritizing_SEH": "prioritizing score+",
                     "vb_eldarica_abstract_off_prioritizing_rank": "Prioritizing score",
                     "vb_eldarica_abstract_off_pruning_rank": "Pruning rank",
                     "vb_eldarica_abstract_off_pruning_score": "Pruning score",
                     "eldarica_symex_original": "Original", "vb_eldarica_symex_prioritize": "Prioritizing score"}
    for pair in comparison_pairs:
        if "symex" in pair[0]:
            engine = "symbolic execution"
        else:
            engine = "predicate abstraction"
        original_solving_time_list = []
        strategy_solving_time_list = []
        satisfiability_list = []
        file_name_list = []
        for name, original_s, strategy_s, original_st, strategy_st in zip(solvability_dict["file_name"],
                                                                          solvability_dict[pair[0] + "_satisfiability"],
                                                                          solvability_dict[pair[1] + "_satisfiability"],
                                                                          solvability_dict[pair[0] + "_solving_time"],
                                                                          solvability_dict[pair[1] + "_solving_time"]):
            if original_s == strategy_s and original_s != "unknown":  # and original_s == "unsafe":
                file_name_list.append(name)
                satisfiability_list.append(original_s)
                original_solving_time_list.append(original_st)
                strategy_solving_time_list.append(strategy_st)

        scatter_plot(x_data=original_solving_time_list, y_data=strategy_solving_time_list, z_data=satisfiability_list,
                     x_axis=axis_name_map[pair[0]], y_axis=axis_name_map[pair[1]], folder=scatter_folder,
                     data_text=file_name_list,
                     name="Solving time (second)" + "<br>Solver engine: " + engine, scale="log")


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
