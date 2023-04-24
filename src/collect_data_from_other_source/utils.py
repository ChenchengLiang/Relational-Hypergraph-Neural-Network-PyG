import time
import subprocess
import json
import os
import glob
from src.utils import get_file_list, unzip_file, compress_file, make_dirct, unzip_relative_files, comress_relative_files
import os
from tqdm import tqdm
from src.CONSTANTS import benchmark_timeout
from shutil import copy, move


def collect_solving_info_from_other_solvers(folder, solver_location="z3", shell_timeout=benchmark_timeout,
                                            solver_name="z3", solver_parameter=" "):
    if solver_name == "z3":
        solver_parameter = "-smt2 "
    elif solver_name == "golem":
        solver_parameter = " "
    else:
        pass
    # elif solver_name == "eld":
    #     solver_parameter = " -abstract:relIneqs "

    shell_folder = make_dirct(os.path.join(os.path.dirname(folder), "shell_folder"))
    file_list = [x.strip(".zip") for x in get_file_list(folder, "smt2")]
    file_list_dict = {f: [] for f in file_list}
    # add pruned and simplified files
    for index in file_list:
        file_list_dict[index] = file_list_dict[index] + [index + ".zip"]
        if len(glob.glob(index + ".pruned*"))!=0:
            file_list_dict[index] = file_list_dict[index] + glob.glob(index + ".pruned*")
        if os.path.exists(index + ".simplified.zip"):
            file_list_dict[index] = file_list_dict[index] + [index + ".simplified.zip"]
    print("file_list_dict", file_list_dict)
    timeout_command = "timeout " + str(shell_timeout)
    for index_file in tqdm(file_list_dict, desc="progress"):
        # unzip file
        unzip_relative_files(index_file, delete_original_zip_file=True)
        for f in file_list_dict[index_file]:
            f=f.strip(".zip")
            # change file name if it is not end with .smt2
            if (not f.endswith(".smt2")):
                move(f, f + ".smt2")
                smt2_file = f + ".smt2"
            else:
                smt2_file = f

            base_file_name = os.path.basename(smt2_file)
            print("base_file_name", base_file_name)
            shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + base_file_name + ".sh"

            # write shell file
            with open(shell_file_name, "w") as ff:
                ff.write("#!/bin/sh\n")
                ff.write(
                    timeout_command + " " + solver_location + " " + solver_parameter + " " + smt2_file + " " + "\n")

            # run shell
            log_file = folder + "/" + base_file_name + "." + solver_name + "-solvability.JSON"
            run_one_shell(shell_file_name, log_file=log_file,solver_parameter=solver_parameter)
            compress_file([log_file], log_file + ".zip")
            os.remove(log_file)

            # remove shell file
            os.remove(shell_file_name)
            if (not f.endswith(".smt2")):
                move(smt2_file, smt2_file[:-len(".smt2")])

        # zip file again
        comress_relative_files(index_file, delete_original_file=True)


def run_one_shell(shell_file_name, log_file,solver_parameter=" "):
    initiall_dict = {"solving_time": [str(benchmark_timeout)], "satisfiability": ["-1"]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(initiall_dict, outfile, indent=4)

    run_shell_command = ["sh", shell_file_name]
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.PIPE, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    output = eld.stdout.read().decode('utf-8').strip()

    out_dict = {"solving_time": [str(used_time)], "satisfiability": [output],"solver_parameter":[solver_parameter]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(out_dict, outfile, indent=4)

    return used_time
