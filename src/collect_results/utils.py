from src.utils import unzip_file, make_dirct, convert_bytes
import os
import json
import glob
from shutil import copy
from tqdm import tqdm
from src.utils import select_key_with_value_condition


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


def read_files(file_list, file_type="solvability.JSON", read_function=read_json_file):
    for file in tqdm(file_list, desc="read " + file_type):
        file_name = file[:-len(".zip")]
        json_file = file_name + "." + file_type if len(file_type) != 0 else file_name
        unzip_file(json_file + ".zip")
        json_obj = {}
        json_obj["file_name"] = json_file[:-len(file_type) - 1]
        json_obj["file_size"] = os.path.getsize(json_file)
        json_obj["file_size_h"] = convert_bytes(os.path.getsize(json_file))
        if os.path.exists(json_file):
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
    solving_option, min_solving_time = select_key_with_value_condition(solving_time_dict, func)
    solving_time_cegar_interation_number = int(
        object[solving_option.replace("solvingTime", "cegarIterationNumber")][0])
    solving_time_generated_predicate_number = int(
        object[solving_option.replace("solvingTime", "generatedPredicateNumber")][0])
    solving_time_average_predicate_size = int(
        object[solving_option.replace("solvingTime", "averagePredicateSize")][0])
    solving_time_predicate_generator_time = int(
        object[solving_option.replace("solvingTime", "predicateGeneratorTime")][0])

    data_dict[func.__name__ + "_solving_time_option"].append(solving_option.replace("solvingTime_", ""))
    data_dict[func.__name__ + "_solving_time (s)"].append(min_solving_time / 1000)
    data_dict[func.__name__ + "_solving_time_cegar_interation_number"].append(
        solving_time_cegar_interation_number)
    data_dict[func.__name__ + "_solving_time_generated_predicate_number"].append(
        solving_time_generated_predicate_number)
    data_dict[func.__name__ + "_solving_time_average_predicate_size"].append(
        solving_time_average_predicate_size)
    data_dict[func.__name__ + "_solving_time_predicate_generator_time"].append(
        solving_time_predicate_generator_time)
    return solving_option
