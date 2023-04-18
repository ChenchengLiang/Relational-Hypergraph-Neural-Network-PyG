import sys

from src.experiment_utils import run_one_experiment
from src.layers import HyperConv

def main():
    folder_name = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/one-example-demo-unsatcore-CDHG"#sys.argv[1]
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
                                ],"epochs":100,"patient":50}

    benchmarks = [folder_name]

    # load data
    for _benchmark in benchmarks:
        run_one_experiment(params)


if __name__ == '__main__':
    main()
