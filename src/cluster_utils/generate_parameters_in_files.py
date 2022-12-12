import sys
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
#sys.path.append("../..")
from src.layers import HyperConv
from src.utils import make_dirct
from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
import json
from shutil import rmtree
def main():

    benchmarks = [sys.argv[1], sys.argv[2]]
    parameter_folder = "/cephyr/users/liangch/Alvis/training_code/hyper-parameters"
    # benchmarks=["/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CDHG",
    #             "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CG"]
    # parameter_folder = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/hyper-parameters"


    parameter_folder = make_dirct(parameter_folder)
    rmtree(parameter_folder)
    parameter_folder= make_dirct(parameter_folder)

    experiment_date = True
    models = ["hyper_GCN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification","unsat_core_binary_classification"]
    tasks = ["unsat_core_binary_classification"]
    num_gnn_layers = [2]
    dropout_rate = {"gnn_dropout_rate": 0.2, "mlp_dropout_rate": 0.1}
    num_linear_layers = [4]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [True, False]
    add_backward_edges = [False]
    add_global_edges = [False]
    self_loop = [False]
    epochs = 1
    reload_data = False
    fix_random_seed = True
    use_class_weight = True

    parameter_dict_list=[]

    for benchmark in benchmarks:
        for model in models:
            for task in tasks:
                for num_gnn_layer in num_gnn_layers:
                    for data_shuffle in data_loader_shuffle:
                        for _self_loop in self_loop:
                            for num_linear_layer in num_linear_layers:
                                if model == "GNN":
                                    for gnn in gnns:
                                        parameter_dict_list.append({"model":model, "task":task, "num_gnn_layer":num_gnn_layer,
                                                                    "benchmark":benchmark, "data_shuffle":data_shuffle,
                                                                    "gnn":gnn.__name__, "use_intermediate_gnn_results":False,
                                                                    "epochs":epochs, "file_name":"", "reload_data":True,
                                                                    "self_loop":True, "add_backward_edges":False,"add_global_edges":False,
                                                                    "fix_random_seeds":fix_random_seed,"experiment_date":experiment_date,
                                                                    "dropout_rate":dropout_rate,"num_linear_layer":4,"use_class_weight":True})


                                else:
                                    for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                        for _add_backward_edge in add_backward_edges:
                                            for _add_global_edge in add_global_edges:
                                                parameter_dict_list.append(
                                                    {"model": model, "task": task, "num_gnn_layer": num_gnn_layer,
                                                     "benchmark": benchmark, "data_shuffle": data_shuffle,
                                                     "gnn": HyperConv.__name__, "use_intermediate_gnn_results": _use_intermediate_gnn_results,
                                                     "epochs": epochs, "file_name": "", "reload_data": reload_data,
                                                     "self_loop": _self_loop, "add_backward_edges": _add_backward_edge,
                                                     "add_global_edges": _add_global_edge,
                                                     "fix_random_seeds": fix_random_seed,
                                                     "experiment_date": experiment_date,
                                                     "dropout_rate": dropout_rate, "num_linear_layer": num_linear_layer,
                                                     "use_class_weight": use_class_weight})


    for i,parameter_dict in enumerate(parameter_dict_list):
        with open(parameter_folder+"/hyper-paprameter_"+str(i)+".JSON", 'w') as f:
            json.dump(parameter_dict, f, indent=4, sort_keys=True)



if __name__ == '__main__':
    main()
