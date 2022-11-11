from src.utils import get_file_list,unzip_file,make_dirct,compress_file
import os
from utils import run_one_shell
def main():
    folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/z3-non-linear-unsolvable/test"
    shell_timeout= 60 * 5
    shell_folder = make_dirct(os.path.join(os.path.dirname(folder), "shell_folder"))
    timeout_command = "timeout " + str(shell_timeout)
    for file in get_file_list(folder, "smt2"):
        file_name = file[:-len(".zip")]
        template_name=file_name+".tpl"

        unzip_file(file)
        os.remove(file)


        shell_file_name = shell_folder + "/" + "run-ulimit" + "-" + os.path.basename(file_name) + ".sh"
        solver_location="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/eldarica-graph-generation/eld"
        solver_parameter_list = "-postHints:"+template_name
        log_parameters=""
        with open(shell_file_name, "w") as ff:
            ff.write("#!/bin/sh\n")
            ff.write(
                timeout_command + " " + solver_location + " " + file_name + " " + solver_parameter_list + log_parameters + "\n")

        log_file = folder + "/" + file_name + ".log"
        run_one_shell(shell_file_name,log_file=log_file)

        # remove shell file and zip file again
        os.remove(shell_file_name)
        compress_file([file_name], file_name + ".zip")
        os.remove(file_name)

if __name__ == '__main__':
    main()