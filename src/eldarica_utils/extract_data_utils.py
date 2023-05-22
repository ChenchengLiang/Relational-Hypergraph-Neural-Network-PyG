

import sys
sys.path.append("../..")
from src.utils import make_dirct,compress_file,unzip_file,get_file_list
import os
import time
import subprocess
import glob
import json
import numpy as np
from shutil import copy, move


def run_eldarica_with_shell(file, shell_timeout, solver_parameter_list, shell_folder,solver_location = "../../eldarica-graph-generation/eld "):
    file = file[:-len(".zip")]

    # unzip file
    for f in glob.glob(file + "*.zip"):
        unzip_file(f)
        os.remove(f)

    file_name = os.path.basename(file)
    shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + file_name + ".sh"
    solver_parameter_list= change_eldarica_parameters(file, solver_parameter_list) if "eldarica" in solver_location else solver_parameter_list
    timeout_command = "timeout " + str(shell_timeout)
    f = open(shell_file_name, "w")
    f.write("#!/bin/sh\n")
    # f.write("ulimit -m 4000000; \n")
    # f.write("ulimit -v 6000000; \n")
    # f.write("ulimit -a; \n")
    f.write(timeout_command + " " + solver_location + " " + file + " " + solver_parameter_list + "\n")
    f.close()

    run_shell_command = ["sh", shell_file_name]
    used_time = call_solver_one_time(run_shell_command, file_name, solver_parameter_list)
    # os.remove(shell_file_name)

    # compress files
    if os.path.exists(file):
        file_list = glob.glob(file + "*")
        for f in file_list:
            if "out.gz" not in f:
                compress_file([f], f + ".zip")
                os.remove(f)


def call_solver_one_time(run_shell_command, file_name, solver_parameter_list):
    print("-" * 20)
    print("extracting " + file_name, solver_parameter_list)
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.DEVNULL, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    print("extracting " + file_name + " finished", "use time: ", used_time)
    return used_time

def change_eldarica_parameters(file, params):
    if "mineTemplates" in params or "mineCounterExample" in params:
        params = params + get_eldarica_option_by_shortest_solving_Time(file)
    return params


def get_eldarica_option_by_shortest_solving_Time(file):
    # use abstract option according to solving time
    json_file = file + ".solvability.JSON"
    if os.path.exists(json_file):
        abstracOptionDict = {
            "solvingTime_Octagon_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:oct -splitClauses:1 ",
            "solvingTime_Term_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:term -splitClauses:1 ",
            "solvingTime_RelationalEqs_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:relEqs -splitClauses:1 ",
            "solvingTime_RelationalIneqs_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:relIneqs -splitClauses:1 ",
            "solvingTime_Off_CDHG_off_0.0_splitClauses_1_cost_same": " -abstract:off -splitClauses:1 ",
            # "solvingTime_Octagon_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:oct -splitClauses:0 ",
            # "solvingTime_Term_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:term -splitClauses:0 ",
            # "solvingTime_RelationalEqs_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:relEqs -splitClauses:0 ",
            # "solvingTime_RelationalIneqs_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:relIneqs -splitClauses:0 ",
            # "solvingTime_Octagon_CDHG_off_0.0_splitClauses_0_cost_same": " -abstract:oct -splitClauses:0 ",
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