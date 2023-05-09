import sys

#sys.path.append("../..")
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG") #local machine path
from src.utils import get_file_list, unzip_file, compress_file, make_dirct
import os
from tqdm import tqdm
from utils import run_one_shell,collect_solving_info_from_other_solvers
from src.CONSTANTS import benchmark_timeout

def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/supplimentary/train_data" #sys.argv[1]
    solver_location = "/home/cheli243/Desktop/CodeToGit/eldarica-fork-symex/assembly/eld"#sys.argv[2]
    try:
        solver_parameter = "-abstract:off -sym:1 "#sys.argv[3] #-abstract:off -sym:1 -hornGraphType:CG
    except:
        solver_parameter = " "

    collect_solving_info_from_other_solvers(folder, solver_location=solver_location, shell_timeout=60*20, solver_name=os.path.basename(solver_location),solver_parameter=solver_parameter) #z3




if __name__ == '__main__':
    main()