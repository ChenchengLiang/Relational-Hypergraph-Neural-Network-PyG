import sys
sys.path.append("../..")
from src.utils import get_file_list,unzip_file,make_dirct,compress_file
from src.collect_results.utils import copy_relative_files
import os
from tqdm import tqdm
from utils import run_one_shell
def main():
    folder=sys.argv[1]#"/home/cheli243/PycharmProjects/HintsLearning/benchmarks/z3-non-linear-unsolvable/train_data-solved"
    solver_location =sys.argv[2] #"/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/eldarica-graph-generation/eld"

    shell_timeout= 60 * 5
    shell_folder = make_dirct(os.path.join(os.path.dirname(folder), "shell_folder"))
    timeout_command = "timeout " + str(shell_timeout)
    solvable_folder=make_dirct(folder+"-eldarica-solvable")
    unsolvable_folder = make_dirct(folder + "-eldarica-unsolvable")
    template_empty_folder = make_dirct(folder + "-no-template")

    #separate empty template
    for zip_file_name in tqdm(get_file_list(folder, "smt2"), desc="progress"):
        file_name = zip_file_name[:-len(".zip")]
        template_name = file_name + ".tpl"
        with open(template_name, "r") as t:
            if len(t.read())==0:
                copy_relative_files(file_name,template_empty_folder)
    #separate solvable and usolvable
    for zip_file_name in tqdm(get_file_list(folder, "smt2"),desc="separate solvable and usolvable pregress"):
        file_name = zip_file_name[:-len(".zip")]
        template_name=file_name+".tpl"
        base_file_name=os.path.basename(file_name)

        unzip_file(zip_file_name)
        os.remove(zip_file_name)


        shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + base_file_name + ".sh"
        solver_parameter_list = " -postHints:"+template_name +" -log "
        log_parameters=" 2>&1 | "  + " tee " + file_name + ".eldarica.log"
        with open(shell_file_name, "w") as ff:
            ff.write("#!/bin/sh\n")
            ff.write(
                timeout_command + " " + solver_location + " " + file_name + " " + solver_parameter_list + log_parameters + "\n")

        used_time=run_one_shell(shell_file_name,log_file=file_name + ".log")


        # remove shell file and zip file again
        os.remove(shell_file_name)
        compress_file([file_name], file_name + ".zip")
        os.remove(file_name)

        if used_time>shell_timeout:
            copy_relative_files(file_name,unsolvable_folder)
        else:
            copy_relative_files(file_name,solvable_folder)

if __name__ == '__main__':
    main()