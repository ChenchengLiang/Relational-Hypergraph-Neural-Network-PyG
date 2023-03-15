import sys

#sys.path.append("../..")
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG") #local machine path
from src.utils import get_file_list, unzip_file, compress_file, make_dirct
import os
from tqdm import tqdm
from utils import run_one_shell,collect_solving_info_from_other_solvers

def main():
    folder = sys.argv[1]
    solver_location = sys.argv[2]
    collect_solving_info_from_other_solvers(folder, solver_location=solver_location, shell_timeout=20,solver_name=os.path.basename(solver_location)) #z3




if __name__ == '__main__':
    main()