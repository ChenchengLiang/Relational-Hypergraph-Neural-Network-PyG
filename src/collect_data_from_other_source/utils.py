import time
import subprocess
import json
import os

from src.utils import get_file_list, unzip_file, compress_file, make_dirct
import os
from tqdm import tqdm


def collect_solving_info_from_other_solvers(folder,solver_location="z3", shell_timeout=20,solver_name="z3"):
    solver_parameter_list =  "-smt2 " if  solver_name=="z3" else " "
    if solver_name == "z3":
        solver_parameter_list = "-smt2 "
    elif solver_name == "golem":
        solver_parameter_list = " "
    elif solver_name == "eld":
        solver_parameter_list = " -abstract:term "

    shell_folder = make_dirct(os.path.join(os.path.dirname(folder), "shell_folder"))
    file_list = get_file_list(folder, "smt2")
    timeout_command = "timeout " + str(shell_timeout)
    for f in tqdm(file_list, desc="progress"):
        # unzip file
        unzip_file(f)
        f = f[:-len(".zip")]
        # print info
        base_file_name = os.path.basename(f)
        print("base_file_name", base_file_name)
        shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + base_file_name + ".sh"

        # write shell file
        with open(shell_file_name, "w") as ff:
            ff.write("#!/bin/sh\n")
            ff.write(
                timeout_command + " " + solver_location + " "+ solver_parameter_list  +" " + f + " "  + "\n")

        # run shell
        log_file = folder + "/" + base_file_name + "."+solver_name +"-solvability.JSON"
        run_one_shell(shell_file_name, log_file=log_file)
        compress_file([log_file],log_file + ".zip")
        os.remove(log_file)

        # remove shell file and zip file again
        os.remove(shell_file_name)
        compress_file([f], f + ".zip")
        os.remove(f)

def run_one_shell(shell_file_name, log_file):
    initiall_dict = {"solving_time": ["10800"], "satisfiability": ["-1"]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(initiall_dict, outfile,indent=4)

    run_shell_command = ["sh", shell_file_name]
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.PIPE, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    output = eld.stdout.read().decode('utf-8').strip()

    out_dict={"solving_time":[str(used_time)],"satisfiability":[output]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(out_dict, outfile,indent=4)


    return used_time
