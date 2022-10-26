from ..utils import get_file_list
import sys
import os
import time
import subprocess
import glob
import json
import numpy as np
def main():

    parameters_pipeline = []
    shell_timeout = int(60 * 60 * 3)
    eldarica_timeout = 60 * 60 * 3
    abstract_options=["empty","term","oct","relEqs","relIneqs"]
    split_clause_option=["1"] #["0","1"]
    data_fold=["train_data","valid_data","test_data"]
    file_type="smt2"


    #get getSolvability # 15 hours
    for a in abstract_options:
        for s in split_clause_option:
            parameters_pipeline.append(" -getSolvability " + " -abstract:"+a+ " -splitClauses:"+s + " -t:"+str(eldarica_timeout))


    #get labeled templates # 3 hours
    parameters_pipeline.append(" -mineTemplates ")

    #construct graphs # 6 hours
    parameters_pipeline.append(" -getHornGraph:CDHG ")
    parameters_pipeline.append(" -getHornGraph:CG ")

    #todo check solvability for predicted templates


    benchmark_name = "../../benchmarks/" + sys.argv[1]
    shell_folder=os.path.join(benchmark_name,"shell_files")
    make_dirct(shell_folder)
    for eldarica_parameters in parameters_pipeline:
        for fold in data_fold:
            file_list=get_file_list(os.path.join(benchmark_name,fold),file_type)
            for file in file_list:
                run_eldarica_with_shell(file,shell_timeout,eldarica_parameters,shell_folder)




def run_eldarica_with_shell(file,shell_timeout,eldarica_parameter_list,shell_folder):
    file = file[:-len(".zip")]

    #unzip file
    for f in glob.glob(file + "*"):
        unzip_file(f)
        os.remove(f)

    eldarica = "../../eldarica-graph-generation/eld "
    file_name=os.path.basename(file)
    shell_file_name = shell_folder+"/"+"run-ulimit" + "-" + file_name + ".sh"
    eldarica_parameter_list=change_eldarica_parameters(file,eldarica_parameter_list)
    timeout_command = "timeout " + str(shell_timeout)
    f = open(shell_file_name, "w")
    f.write("#!/bin/sh\n")
    # f.write("ulimit -m 4000000; \n")
    # f.write("ulimit -v 6000000; \n")
    # f.write("ulimit -a; \n")
    f.write(timeout_command+ " " + eldarica + " " + file + " " + eldarica_parameter_list + "\n")
    f.close()

    run_shell_command = ["sh", shell_file_name]
    used_time = call_Eldarica_one_time(run_shell_command, file_name,eldarica_parameter_list)
    #os.remove(shell_file_name)

    # compress files
    if os.path.exists(file):
        file_list = glob.glob(file + "*")
        for f in file_list:
            compress_file([f], f + ".zip")
            os.remove(f)


def call_Eldarica_one_time(run_shell_command, file_name,eldarica_parameter_list):
    print("-" * 20)
    print("extracting " + file_name, eldarica_parameter_list)
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.DEVNULL, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    print("extracting " + file_name + " finished", "use time: ", used_time)
    return used_time


def compress_file(inp_file_names, out_zip_file):
    import zipfile
    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(out_zip_file, mode="w")
    try:
        for file_to_write in inp_file_names:
            zf.write(file_to_write, os.path.basename(out_zip_file)[:-len(".zip")], compress_type=compression)
    except FileNotFoundError as e:
        print(str(e))
    finally:
        zf.close()


def unzip_file(zip_file):
    if os.path.exists(zip_file):
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file))
    else:
        print("zip file " + zip_file + " not existed")


def change_eldarica_parameters(file,params):
    if "mineTemplates" in params:
        params=params+get_eldarica_option_by_shortest_solving_Time(file)
    return params

def get_eldarica_option_by_shortest_solving_Time(file):
    # use abstract option according to solving time
    json_file = file + ".solvability.JSON"
    if os.path.exists(json_file):
        abstracOptionDict = {"solvingTime_Octagon_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:oct -splitClauses:1 ",
                             "solvingTime_Term_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:term -splitClauses:1 ",
                             "solvingTime_RelationalEqs_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:relEqs -splitClauses:1 ",
                             "solvingTime_RelationalIneqs_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:relIneqs -splitClauses:1 ",
                             "solvingTime_Off_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:off -splitClauses:1 ",
                             # "solvingTime_Octagon_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:oct -splitClauses:0 ",
                             # "solvingTime_Term_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:term -splitClauses:0 ",
                             # "solvingTime_RelationalEqs_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:relEqs -splitClauses:0 ",
                             # "solvingTime_RelationalIneqs_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:relIneqs -splitClauses:0 ",
                             #"solvingTime_Octagon_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:oct -splitClauses:0 ",
                             }
        maxKeyValue = ["", 60 * 60 * 3 * 1000 * 10]
        with open(json_file) as f:
            loaded_content = json.load(f)
            for k in loaded_content:
                if k in abstracOptionDict.keys():
                    solvingTime = int(np.array(loaded_content[k])[0])
                    if solvingTime < maxKeyValue[1]:
                        maxKeyValue[0] = k
                        maxKeyValue[1] = solvingTime
        print(os.path.basename(file), "maxKeyValue", maxKeyValue[0], ":", maxKeyValue[1])
        return abstracOptionDict[maxKeyValue[0]]


def make_dirct(d):
    try:
        os.mkdir(d)
    except:
        print(str(d), "folder existed")
if __name__ == '__main__':
    main()