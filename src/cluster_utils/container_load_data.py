import sys

# sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.experiment_utils import run_one_experiment
from src.layers import HyperConv
from utils import get_task_by_folder_name


def main():
    folder_name = sys.argv[1]
    params = {"benchmark": folder_name, "experiment_date": True, "experiment_name": "load_data", "reload_data": True,
              "gnn": HyperConv.__name__, "cdhg_edge_types": ["relationSymbolArgumentEdge", "guardEdge",
                                                             "ASTLeftEdge", "ASTRightEdge",
                                                             "ASTEdge",
                                                             "quantifierEdge",
                                                             "controlFlowHyperEdge", "dataFlowHyperEdge"],
              "cg_edge_types": ["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
                                "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge",
                                "ASTLeftEdge", "ASTRightEdge",
                                "ASTEdge",
                                "quantifierEdge",
                                "guardEdge", "dataEdge",
                                ],"epochs":1,"patient":1}

    benchmarks = [folder_name]

    # load data
    for _benchmark in benchmarks:
        run_one_experiment(params)


if __name__ == '__main__':
    main()
