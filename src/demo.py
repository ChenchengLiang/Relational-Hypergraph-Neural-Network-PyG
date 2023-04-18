import sys
sys.path.append("../")
#sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.experiment_utils import run_one_experiment
from src.layers import HyperConv

def main():
    #folder_name can be replaced to a absolute path to the dataset folder, for instance "/home/path_to/one-example-demo-unsatcore-CDHG"
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
                                ],"epochs":100,"patient":50}

    run_one_experiment(params)


if __name__ == '__main__':
    main()
