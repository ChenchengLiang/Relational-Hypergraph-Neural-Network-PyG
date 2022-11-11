import sys

sys.path.append("../..")
from src.utils import get_file_list, unzip_file, compress_file, make_dirct
from src.collect_results.utils import copy_relative_files
import os
from tqdm import tqdm
from utils import run_one_shell

def main():
    folder = sys.argv[1]
    collect_predicate_from_other_solvers(folder, solver_location=sys.argv[2], shell_timeout=60 * 5)
    separate_solvable_cases(folder)


def separate_solvable_cases(folder):
    folder_base_name = os.path.basename(folder)
    solvable_folder = make_dirct(os.path.dirname(folder) + "/" + folder_base_name + "-solved")
    unsolvable_folder = make_dirct(os.path.dirname(folder) + "/" + folder_base_name + "-unsolved")
    for file in get_file_list(folder, "smt2"):
        file_name = file[:-len(".zip")]
        with open(file_name + ".predicates", "r") as f:
            content = f.read()
            if len(content) != 0:
                # transform to initial predicate
                copy_relative_files(file_name, solvable_folder)
                tpl_file_content = content.replace("define-fun", "initial-predicates").replace(") Bool", ")")
                with open(solvable_folder + "/" + os.path.basename(file_name) + ".tpl", "w") as template_file:
                    template_file.write(tpl_file_content)

            else:
                copy_relative_files(file_name, unsolvable_folder)


def collect_predicate_from_other_solvers(unsolvable_folder, solver_location="z3", shell_timeout=20):
    solver_parameter_list = " -smt2 -v:1 "
    shell_folder = make_dirct(os.path.join(os.path.dirname(unsolvable_folder), "shell_folder"))
    file_list = get_file_list(unsolvable_folder, "smt2")
    timeout_command = "timeout " + str(shell_timeout)
    for f in tqdm(file_list, desc="progress"):
        # for f in file_list:
        # unzip file
        unzip_file(f)
        os.remove(f)
        f = f[:-len(".zip")]

        # print info
        file_name = os.path.basename(f)
        print("file_name", file_name)

        # set shell parameters
        filter_key_words_list = ["transform", "expand", "spacer", "Propagating", "Entering", "create_child", "sat"]
        str_filter = ""
        for kw in filter_key_words_list:
            str_filter = str_filter + " grep -v \"" + kw + "\" | "
        log_parameters = " 2>&1 | " + str_filter + " tee " + unsolvable_folder + "/" + file_name + ".predicates"
        shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + file_name + ".sh"

        # write shell file
        with open(shell_file_name, "w") as ff:
            ff.write("#!/bin/sh\n")
            ff.write(
                timeout_command + " " + solver_location + " " + f + " " + solver_parameter_list + log_parameters + "\n")

        # run shell
        log_file=unsolvable_folder + "/" + file_name + ".log"
        run_one_shell(shell_file_name, log_file=log_file)

        # remove shell file and zip file again
        os.remove(shell_file_name)
        compress_file([f], f + ".zip")
        os.remove(f)




if __name__ == '__main__':
    main()
