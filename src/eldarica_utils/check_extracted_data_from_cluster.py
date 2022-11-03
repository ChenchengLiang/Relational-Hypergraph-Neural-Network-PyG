import os.path
from shutil import copy
from src.utils import get_file_list, make_dirct
import glob
import gzip
from src.collect_results.utils import read_files, read_json_file


def main():
    # # for constructed graphs
    # separate_corner_cases_from_cluster_graph_construction(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-graphs/train_data",
    #     file_numebr=10, target_message="not-timeout-cases")
    # #for mined templates
    # separate_corner_cases_from_cluster_mineTemplates(folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-labeled-divided-2454/train_data",
    #                              file_numebr=6,target_message="ready_for_check_other_issues")

    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-graphs/train_data"
    check_cluster_log_files(os.path.dirname(folder) + "/log", "out", "gz", "chc-LIA-Lin_0636.smt2 ")


def separate_corner_cases_from_cluster_mineTemplates(folder, file_numebr, target_message):
    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder)
    separated_folder = separate_cluster_timeout_case(zip_file_folder, file_number=file_numebr,
                                                     target_message=target_message)


def separate_corner_cases_from_cluster_graph_construction(folder, file_numebr, target_message):
    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder)
    separated_folder = separate_cluster_timeout_case(zip_file_folder, file_number=file_numebr,
                                                     target_message=target_message)
    separated_folder = separate_cases_by_graph_field(separated_folder, "non-trivial-clauses","no_simplified_clauses_folder",separate_no_simplified_clauses)
    separated_folder = separate_cases_by_graph_field(separated_folder, "ready_for_training","no_template_folder",separate_no_template_cases)

def separate_no_simplified_clauses(g,file_name,target_folder,exception_folder):
    if g["nodeNumber"][0] <= 7:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)

def separate_no_template_cases(g,file_name,target_folder,exception_folder):
    if g["templateEdgeNumber"][0] == 1:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)

def separate_cases_by_graph_field(folder, target_folder_name, exception_folder_name,separate_function):
    target_folder = make_dirct(os.path.dirname(folder) + "/" + target_folder_name)
    exception_folder = make_dirct(os.path.dirname(folder) + "/"+exception_folder_name)
    graph_dict_list = read_files(get_file_list(folder, "smt2"), file_type="hyperEdgeGraph.JSON",
                                 read_function=read_json_file)
    try:
        for g in graph_dict_list:
            file_name = g["file_name"][:g["file_name"].find(".hyperEdgeGraph.JSON")]
            separate_function(g,file_name,target_folder,exception_folder)
    except:
        print("file existed")

    return target_folder


def separate_cluster_timeout_case(folder, file_number, target_message="graph_construction_folder"):
    separated_folder = make_dirct(os.path.dirname(folder) + "/" + target_message)
    cluster_timeout_folder = make_dirct(os.path.dirname(folder) + "/cluster_timeout_folder")
    file_dict = {f: glob.glob(f[:-len(".zip")] + "*") for f in get_file_list(folder, "smt2")}
    ready_for_graph_construction_number = 0
    cluster_timeout_number = 0
    try:
        for k in file_dict:
            if len(file_dict[k]) == file_number:
                ready_for_graph_construction_number += 1
                for ff in file_dict[k]:
                    copy(ff, separated_folder)
            else:
                cluster_timeout_number += 1
                for ff in file_dict[k]:
                    copy(ff, cluster_timeout_folder)
    except:
        print("file existed")
    print(target_message + "_number", ready_for_graph_construction_number)
    print("cluster_timeout_number", cluster_timeout_number)
    return separated_folder


def separate_zip_and_unzip_files(folder):
    zip_file_list = get_file_list(folder, "smt2")
    print("ziped_smt2_file_list", len(zip_file_list))

    unziped_file_list = glob.glob(folder + "/" + "*.smt2")
    print("unziped_file_list", len(unziped_file_list))

    zip_file_folder = make_dirct(os.path.dirname(folder) + "/" + "zip_files")
    unzip_file_folder = make_dirct(os.path.dirname(folder) + "/" + "unzip_files")

    try:
        for f in glob.glob(folder + "/*"):
            if "zip" in f:
                copy(f, zip_file_folder)
            else:
                copy(f, unzip_file_folder)
    except:
        print("file existed")
    zip_file_list = glob.glob(zip_file_folder + "/*")
    unzip_file_list = glob.glob(unzip_file_folder + "/*")
    print("files in zip file folder", len(zip_file_list))
    print("files in unzip file folder", len(unzip_file_list))

    # for f in unzip_file_list:
    #     check_cluster_log_files(os.path.dirname(folder)+"/log","out","gz",f)
    return zip_file_folder, unzip_file_folder


def check_cluster_log_files(folder, file_type, compress_type, smt2_file):
    # print relation between .out and .smt2 files
    smt2_file = os.path.basename(smt2_file)
    file_list = get_file_list(folder, file_type, compress_type)
    for file in file_list:
        with gzip.open(file, 'rb') as f:
            file_content = f.read()
            file_content = file_content.decode("utf-8")
            if smt2_file in file_content:
                print("file", smt2_file)
                print("out file", file)
                print(file_content)


def copy_relative_files(file_name, folder):
    for f in glob.glob(file_name + "*"):
        copy(f, folder)


if __name__ == '__main__':
    main()
