import sys

#sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG") #local machine path
sys.path.append("/home/cheli243/Systematic-Predicate-Abstraction-using-Machine-Learning/extractable_dataset") #uppmax path
import os
from src.collect_data_from_other_source.utils import collect_solving_info_from_other_solvers
from src.CONSTANTS import benchmark_timeout

def main():
    folder = sys.argv[1]
    solver_location = sys.argv[2]
    collect_solving_info_from_other_solvers(folder, solver_location=solver_location, shell_timeout=benchmark_timeout,
                                            solver_name=os.path.basename(solver_location))  # z3solver_location = sys.argv[2]



if __name__ == '__main__':
    main()