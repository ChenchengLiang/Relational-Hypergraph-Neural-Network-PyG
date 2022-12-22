import sys

sys.path.append("/cephyr/users/liangch/Alvis/training_code")
# sys.path.append("../..")
from src.layers import HyperConv
from src.utils import make_dirct
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
import json
from shutil import rmtree
from utils import get_task_by_folder_name


def main():
    folder_1 = sys.argv[1]
    folder_2 = sys.argv[2]
    benchmarks = [folder_1, folder_2]
    parameter_folder = "/cephyr/users/liangch/Alvis/training_code/hyper-parameters"
    # benchmarks=["/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CDHG",
    #             "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CG"]
    # parameter_folder = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/hyper-parameters"

    parameter_folder = make_dirct(parameter_folder)
    rmtree(parameter_folder)
    parameter_folder = make_dirct(parameter_folder)

    experiment_date = False
    # models = ["hyper_GCN", "GNN"]
    models = ["hyper_GCN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification","unsat_core_binary_classification"]
    task = get_task_by_folder_name(folder_1)
    #todo add inner layer control to graph conv operator
    num_gnn_layers = [2] # 8 works best
    dropout_rate = [ #all 0 works
        {"gnn_dropout_rate": 0.0, "mlp_dropout_rate": 0.0, "gnn_inner_layer_dropout_rate": 0.0},
        #{"gnn_dropout_rate": 0.5, "mlp_dropout_rate": 0.5, "gnn_inner_layer_dropout_rate": 0.5},
        #{"gnn_dropout_rate": 0.4, "mlp_dropout_rate": 0.2, "gnn_inner_layer_dropout_rate": 0.0},
        # {"gnn_dropout_rate": 0.8, "mlp_dropout_rate": 0.8, "gnn_inner_layer_dropout_rate": 0.0}
    ]
    num_linear_layers = [2,4,8] # 2 works
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [False]
    add_backward_edges = [False]
    add_global_edges = [True,False]
    self_loop = [False]
    gradient_clip = [True,False]
    embedding_size=[16,32,64]
    epochs = 200
    reload_data = False
    fix_random_seed = True
    use_class_weight = True
    learning_rate = [0.001]
    activation = ["relu"]  # ["relu","leak_relu", "tanh"]
    cdhg_edge_types = ["relationSymbolArgumentEdge", "guardEdge",
                       #"ASTLeftEdge", "ASTRightEdge",
                       "ASTEdge",
                       #"quantifierEdge",
                       "controlFlowHyperEdge", "dataFlowHyperEdge"]
    cg_edge_types = ["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
                     "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge",
                     #"ASTLeftEdge", "ASTRightEdge",
                     "ASTEdge",
                     #"quantifierEdge",
                     "guardEdge", "dataEdge",
                     ]

    parameter_dict_list = []

    for benchmark in benchmarks:
        for model in models:
            for num_gnn_layer in num_gnn_layers:
                for data_shuffle in data_loader_shuffle:
                    for _self_loop in self_loop:
                        for _gradient_clip in gradient_clip:
                            for _dropout_rate in dropout_rate:
                                for _learning_rate in learning_rate:
                                    for _activation in activation:
                                        for _add_global_edge in add_global_edges:
                                            for num_linear_layer in num_linear_layers:
                                                for _embedding_size in embedding_size:
                                                    if model == "GNN":
                                                        for gnn in gnns:
                                                            parameter_dict_list.append(
                                                                {"model": model, "task": task,
                                                                 "num_gnn_layer": num_gnn_layer,
                                                                 "benchmark": benchmark, "data_shuffle": data_shuffle,
                                                                 "gnn": gnn.__name__,
                                                                 "use_intermediate_gnn_results": False,
                                                                 "epochs": epochs, "file_name": "", "reload_data": True,
                                                                 "self_loop": True, "add_backward_edges": False,
                                                                 "add_global_edges": False,
                                                                 "fix_random_seeds": fix_random_seed,
                                                                 "experiment_date": experiment_date,
                                                                 "dropout_rate": _dropout_rate, "num_linear_layer": 4,
                                                                 "use_class_weight": True,
                                                                 "gradient_clip": _gradient_clip,
                                                                 "add_global_edges": _add_global_edge,
                                                                 "learning_rate": _learning_rate,
                                                                 "activation": _activation,
                                                                 "cdhg_edge_types": cdhg_edge_types,
                                                                 "cg_edge_types": cg_edge_types,
                                                                 "embedding_size":_embedding_size})


                                                    else:
                                                        for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                                            for _add_backward_edge in add_backward_edges:
                                                                parameter_dict_list.append(
                                                                    {"model": model, "task": task,
                                                                     "num_gnn_layer": num_gnn_layer,
                                                                     "benchmark": benchmark,
                                                                     "data_shuffle": data_shuffle,
                                                                     "gnn": HyperConv.__name__,
                                                                     "use_intermediate_gnn_results": _use_intermediate_gnn_results,
                                                                     "epochs": epochs, "file_name": "",
                                                                     "reload_data": reload_data,
                                                                     "self_loop": _self_loop,
                                                                     "add_backward_edges": _add_backward_edge,
                                                                     "add_global_edges": _add_global_edge,
                                                                     "fix_random_seeds": fix_random_seed,
                                                                     "experiment_date": experiment_date,
                                                                     "dropout_rate": _dropout_rate,
                                                                     "num_linear_layer": num_linear_layer,
                                                                     "use_class_weight": use_class_weight,
                                                                     "gradient_clip": _gradient_clip,
                                                                     "learning_rate": _learning_rate,
                                                                     "activation": _activation,
                                                                     "cdhg_edge_types": cdhg_edge_types,
                                                                     "cg_edge_types": cg_edge_types,
                                                                     "embedding_size":_embedding_size})

    for i, parameter_dict in enumerate(parameter_dict_list):
        with open(parameter_folder + "/hyper-paprameter_" + str(i) + ".JSON", 'w') as f:
            json.dump(parameter_dict, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
