import os.path
from shutil import copy
from src.utils import get_file_list ,make_dirct
import glob
import gzip
def main():
    constructed_graphs_from_cluster()
    #mined_tempaltes_from_cluster()

def constructed_graphs_from_cluster():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-for-graph-construction-divided-2210/train_data"

    zip_file_list = get_file_list(folder, "smt2")
    print("ziped_smt2_file_list", len(zip_file_list))

    unziped_file_list = glob.glob(folder + "/" + "*.smt2")
    print("unziped_file_list", len(unziped_file_list))

    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder)

    file_dict = {f: glob.glob(f[:-len(".zip")] + "*") for f in get_file_list(zip_file_folder, "smt2")}

    separate_template_mining_timeout(folder, file_dict, file_number=10,target_message="training")

def mined_tempaltes_from_cluster():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-solvable-divided-2932/train_data"

    zip_file_list = get_file_list(folder, "smt2")
    print("ziped_smt2_file_list", len(zip_file_list))

    unziped_file_list = glob.glob(folder + "/" + "*.smt2")
    print("unziped_file_list", len(unziped_file_list))

    zip_file_folder, unzip_file_folder = separate_zip_and_unzip_files(folder)

    file_dict = {f: glob.glob(f[:-len(".zip")] + "*") for f in get_file_list(zip_file_folder, "smt2")}

    separate_template_mining_timeout(folder, file_dict,file_number=6)



def separate_template_mining_timeout(folder,file_dict,file_number,target_message="graph_construction_folder"):
    ready_for_graph_construction_folder = make_dirct(os.path.dirname(folder) + "/ready_for_"+target_message)
    template_mining_timeout_folder = make_dirct(os.path.dirname(folder) + "/cluster_timeout_folder")
    ready_for_graph_construction_number = 0
    template_mining_timeout_number = 0
    for k in file_dict:
        if len(file_dict[k]) == file_number:
            ready_for_graph_construction_number += 1
            try:
                for ff in file_dict[k]:
                    copy(ff, ready_for_graph_construction_folder)
            except:
                print("file existed")
        else:
            template_mining_timeout_number += 1
            try:
                for ff in file_dict[k]:
                    copy(ff, template_mining_timeout_folder)
            except:
                print("file existed")
    print("ready_for_"+target_message+"a_number", ready_for_graph_construction_number)
    print("cluster_timeout_number", template_mining_timeout_number)

def separate_zip_and_unzip_files(folder):
    zip_file_folder = make_dirct(os.path.dirname(folder)+"/"+"zip_files")
    unzip_file_folder = make_dirct(os.path.dirname(folder) + "/" + "unzip_files")

    try:
        for f in glob.glob(folder+"/*"):
            if "zip" in f:
                copy(f, zip_file_folder)
            else:
                copy(f, unzip_file_folder)
    except:
        print("file existed")
    zip_file_list=glob.glob( zip_file_folder+"/*" )
    unzip_file_list=glob.glob( unzip_file_folder+"/*" )
    print("files in zip file folder", len(zip_file_list))
    print("files in unzip file folder", len(unzip_file_list))

    # for f in unzip_file_list:
    #     check_cluster_log_files(os.path.dirname(folder)+"/log","out","gz",f)
    return zip_file_folder,unzip_file_folder

def check_cluster_log_files(folder,file_type,compress_type,smt2_file):
    #print relation between .out and .smt2 files
    smt2_file=os.path.basename(smt2_file)
    file_list=get_file_list(folder,file_type,compress_type)
    for file in file_list:
        with gzip.open(file, 'rb') as f:
            file_content = f.read()
            file_content=file_content.decode("utf-8")
            if smt2_file in file_content:
                print("file", smt2_file)
                print("out file",file)
                print(file_content)


if __name__ == '__main__':
    main()