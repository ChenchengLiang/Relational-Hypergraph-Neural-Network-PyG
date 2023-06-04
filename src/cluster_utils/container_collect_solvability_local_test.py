import sys

sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG") #local machine path

import os
from src.collect_data_from_other_source.utils import collect_solving_info_from_other_solvers
from src.CONSTANTS import benchmark_timeout

def main():
    # need commpile the solver first
    cegar_solver="/home/cheli243/Desktop/CodeToGit/eldarica-fork-master/assembly/eld"
    symex_solver="/home/cheli243/Desktop/CodeToGit/eldarica-fork-symex/assembly/eld"

    folder = "/home/cheli243/Desktop/debug/symex/4723"
    try:
        #solver_parameter = "-getSolvability -hornGraphLabelType:unsatCore -unsatCoreThreshold:0.0 -hornGraphType:CDHG -prioritizeClausesByUnsatCoreRank -abstract:off"
        solver_parameter = " -abstract:off -sym:1 -hornGraphType:CDHG"
    except:
        solver_parameter = " "
    print("solver_parameter", solver_parameter)
    solver_location =symex_solver if "sym" in solver_parameter else cegar_solver

    collect_solving_info_from_other_solvers(folder, solver_location=solver_location, shell_timeout=benchmark_timeout,
                                            solver_name=os.path.basename(solver_location),solver_parameter=solver_parameter)



if __name__ == '__main__':
    main()