import os.path
import shutil
from shutil import copy
from src.utils import get_file_list, make_dirct,select_key_with_value_condition
import glob
import gzip
from src.collect_results.utils import read_files, read_json_file, copy_relative_files,get_solving_time_dict
from tqdm import tqdm
from src.benchmark_statistics.utils import read_satisfiability


def separate_files_by_solvability_fields(folder):
    solvability_object_list=read_files(get_file_list(folder,"smt2"),"solvability.JSON",read_function=read_json_file)
    folder_base_name=os.path.basename(folder)
    summary_folder=make_dirct(os.path.dirname(folder)+"/"+folder_base_name+"_separate_summary")
    sat_folder=make_dirct(summary_folder+"/SAT")
    sat_has_simplified_clauses_folder = make_dirct(sat_folder + "/has-simplified-clauses")
    sat_no_simplified_clauses_folder = make_dirct(sat_folder + "/no-simplified-clauses")
    unsat_folder=make_dirct(summary_folder+"/UNSAT")
    unsat_has_simplified_clauses_folder = make_dirct(unsat_folder + "/has-simplified-clauses")
    unsat_no_simplified_clauses_folder = make_dirct(unsat_folder+ "/no-simplified-clauses")
    unknown_folder = make_dirct(summary_folder + "/UNKNOWN")
    unknown_with_solvability_folder=make_dirct(unknown_folder+"/solvability")
    unknown_without_solvability_folder = make_dirct(unknown_folder + "/no-solvability")
    for object in solvability_object_list:
        if len(object) > 1: #has solvability file
            min_solving_option, min_solving_time = select_key_with_value_condition(get_solving_time_dict(object), min)
            satisfiability = read_satisfiability(object, min_solving_option=min_solving_option)
            if satisfiability==1: #sat
                if int(object["clauseNumberAfterSimplification"][0])==0:
                    copy_relative_files(object["file_name"], sat_no_simplified_clauses_folder)
                else:
                    copy_relative_files(object["file_name"], sat_has_simplified_clauses_folder)
            elif satisfiability==0: #unsat
                if int(object["clauseNumberAfterSimplification"][0]) == 0:
                    copy_relative_files(object["file_name"], unsat_no_simplified_clauses_folder)
                else:
                    copy_relative_files(object["file_name"], unsat_has_simplified_clauses_folder)
            else: #unknown, has clause info
                copy_relative_files(object["file_name"], unknown_with_solvability_folder)
        else: #unknown, no solvability file clause info (terminate in preprocessing)
            copy_relative_files(object["file_name"], unknown_without_solvability_folder)

def separate_corner_cases_from_cluster_solvability(folder, file_numebr, target_message, source=""):
    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder, source)
    separated_folder = separate_cluster_timeout_case(zip_file_folder, file_number=file_numebr,
                                                     target_message=target_message)

def separate_corner_cases_from_cluster_mineTemplates(folder, file_numebr, target_message, source=""):
    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder, source)
    separated_folder = separate_cluster_timeout_case(zip_file_folder, file_number=file_numebr,
                                                     target_message=target_message)


def separate_corner_cases_from_cluster_graph_construction(folder, file_numebr, target_message, source=""):
    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder, source=source)
    separated_folder = separate_cluster_timeout_case(zip_file_folder, file_number=file_numebr,
                                                     target_message=target_message)
    separated_folder, exception_folder = separate_cases_by_graph_field(separated_folder, "1-has-simplified-clauses",
                                                                       "1-no_simplified_clauses",
                                                                       separate_no_simplified_clauses)
    separated_folder, exception_folder = separate_cases_by_graph_field(separated_folder, "2-has_template",
                                                                       "2-no_labels", separate_no_label_cases)
    separated_folder, exception_folder = separate_cases_by_graph_field(separated_folder, "3-labels_indices_match",
                                                                       "3-labels_indices_mismatch", separate_mismatch_indices_and_label_cases)
    separated_folder, exception_folder = separate_cases_by_graph_field(separated_folder, "4-clause_number_match",
                                                                       "4-clause_number_mismatch",
                                                                       separate_mismatch_label_number_and_clauses_number)
    separated_folder, exception_folder = separate_cases_by_graph_field(separated_folder, "5-has-positive-labels",
                                                                       "5-no-positive-labels",
                                                                       separate_no_labeled_template_cases)
    ready_for_train_folder=make_dirct(os.path.join(folder,"6-ready-for-training"))
    for file in glob.glob(separated_folder+"/*") + glob.glob(exception_folder+"/*"):
        copy(file,ready_for_train_folder)

def separate_no_simplified_clauses(cdhg,cg, file_name, target_folder, exception_folder):
    if cdhg["nodeNumber"][0] <= 7:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)


def separate_no_label_cases(cdhg,cg, file_name, target_folder, exception_folder):
    if cdhg["labelNumber"][0] == 0 or cg["labelNumber"][0] == 0:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)

def separate_mismatch_indices_and_label_cases(cdhg,cg, file_name, target_folder, exception_folder):
    if cdhg["labelNumber"][0] != cdhg["labelIndicesNumber"][0] or cg["labelNumber"][0] != cg["labelIndicesNumber"][0]:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)

def separate_mismatch_label_number_and_clauses_number(cdhg,cg, file_name, target_folder, exception_folder):
    if cdhg["guardIndicesNumber"][0] < int(cdhg["clauseNumberAfterSimplification"][0]) or cg["clauseIndicesNumber"][0] != int(cg["clauseNumberAfterSimplification"][0]):
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)


def separate_no_labeled_template_cases(cdhg,cg, file_name, target_folder, exception_folder):
    if sum(cdhg["labelList"]) == 0 or sum(cg["labelList"]) == 0:
        copy_relative_files(file_name, exception_folder)
    else:
        copy_relative_files(file_name, target_folder)


def separate_cases_by_graph_field(folder, target_folder_name, exception_folder_name, separate_function):
    target_folder = make_dirct(os.path.dirname(folder) + "/" + target_folder_name)
    exception_folder = make_dirct(os.path.dirname(folder) + "/" + exception_folder_name)

    cdhg_graph_dict_list = read_files(get_file_list(folder, "smt2"), file_type="hyperEdgeGraph.JSON",
                                 read_function=read_json_file)
    cg_graph_dict_list = read_files(get_file_list(folder, "smt2"), file_type="monoDirectionLayerGraph.JSON",
                                      read_function=read_json_file)
    solvability_dict_list = read_files(get_file_list(folder, "smt2"), file_type="solvability.JSON",
                                      read_function=read_json_file)
    try:
        for cdhg,cg,solv in tqdm(zip(cdhg_graph_dict_list,cg_graph_dict_list,solvability_dict_list),desc=separate_function.__name__):
            file_name_cdhg = cdhg["file_name"][:cdhg["file_name"].find(".hyperEdgeGraph.JSON")]
            if len(cdhg)>3:
                merged_cdhg={**cdhg,**solv}
                merged_cg = {**cg, **solv}
                separate_function(merged_cdhg,merged_cg, file_name_cdhg, target_folder, exception_folder)
                #separate_function(cdhg, cg, file_name_cdhg, target_folder, exception_folder)
            else:
                print("error: no graph file",file_name_cdhg)
    except:
        print("file existed")


    print(os.path.basename(target_folder), len(get_file_list(target_folder, file_type="smt2")))
    print(os.path.basename(exception_folder), len(get_file_list(exception_folder, file_type="smt2")))
    shutil.rmtree(folder)

    return target_folder, exception_folder


def separate_cluster_timeout_case(folder, file_number, target_message="graph_construction_folder"):
    separated_folder = make_dirct(os.path.dirname(folder) + "/" + target_message)
    cluster_timeout_folder = make_dirct(os.path.dirname(folder) + "/cluster_timeout_folder")
    file_dict = {f: glob.glob(f[:-len(".zip")] + "*") for f in get_file_list(folder, "smt2")}
    ready_for_graph_construction_number = 0
    cluster_timeout_number = 0
    try:
        for k in tqdm(file_dict,desc="separate_cluster_timeout_case"):
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
    shutil.rmtree(folder)

    return separated_folder


def separate_zip_and_unzip_files(folder, source=""):
    train_data_folder = os.path.join(folder, "train_data")
    zip_file_list = get_file_list(train_data_folder, "smt2")
    print("ziped_smt2_file_list", len(zip_file_list))

    unziped_file_list = glob.glob(train_data_folder + "/" + "*.smt2")
    print("unziped_file_list", len(unziped_file_list))

    zip_file_folder = make_dirct(os.path.dirname(train_data_folder) + "/" + "zip_files")
    unzip_file_folder = make_dirct(os.path.dirname(train_data_folder) + "/" + "unzip_files")

    try:
        for f in glob.glob(train_data_folder + "/*"):
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

    collect_cluster_log(folder, zip_file_folder, unzip_file_folder, source)
    return zip_file_folder, unzip_file_folder


def collect_cluster_log(folder, zip_file_folder, unzip_file_folder, source=""):
    cluster_log_list = get_file_list(os.path.join(folder, "log"), "out", "gz")
    zipped_smt2_file_list = get_file_list(zip_file_folder, "smt2")
    unzipped_smt2_file_list = get_file_list(unzip_file_folder, "smt2", "")
    for smt2_file in tqdm(zipped_smt2_file_list, desc="collect log for zipped_smt2_file_list"):
        smt2_file_name = os.path.basename(smt2_file[:-len(".zip")])
        scan_cluster_logs(cluster_log_list, smt2_file_name, zip_file_folder, source)
    for smt2_file in tqdm(unzipped_smt2_file_list, desc="collect log for unzipped_smt2_file_list"):
        smt2_file_name = os.path.basename(smt2_file)
        scan_cluster_logs(cluster_log_list, smt2_file_name, unzip_file_folder, source)


def scan_cluster_logs(cluster_log_list, smt2_file_name, target_folder, source=""):
    for file in cluster_log_list:
        with gzip.open(file, 'rb') as f:
            file_content = f.read()
            file_content = file_content.decode("utf-8")
            if smt2_file_name in file_content:
                suffix = "" if len(source) == 0 else "." + source
                copy(file, target_folder + "/" + smt2_file_name + suffix + ".out.gz")


