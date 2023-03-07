import sys

sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import get_file_list, unzip_file, compress_file, make_dirct
import os
from tqdm import tqdm
from src.collect_data_from_other_source.utils import run_one_shell

def main():
    folder = sys.argv[1]
    collect_solving_info_from_other_solvers(folder, solver_location=sys.argv[2], shell_timeout=60*60*3) #z3





def collect_solving_info_from_other_solvers(folder,solver_location="z3", shell_timeout=20,solver_name="z3"):
    solver_parameter_list = " -smt2 "
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


if __name__ == '__main__':
    main()