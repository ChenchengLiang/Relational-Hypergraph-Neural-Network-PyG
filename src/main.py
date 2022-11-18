from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from experiment_utils import run_one_experiment


def main():
    benchmarks = ["../data/linear_dataset_shuffled-CDHG","../data/linear_dataset_shuffled-CG"]
    #models = ["hyper_GCN", "GNN"]
    models = ["hyper_GCN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification"]
    tasks = ["template_binary_classification"]
    num_gnn_layers = [2]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [False]
    self_loop = [True]
    epochs = 5
    reload_data = True

    for model in models:
        for bench in benchmarks:
            for task in tasks:
                for num_gnn_layer in num_gnn_layers:
                    for data_shuffle in data_loader_shuffle:
                        for _self_loop in self_loop:
                            if model == "GNN":
                                for _gnn in gnns:
                                    run_one_experiment(model, task, num_gnn_layer, bench, data_shuffle,
                                                       _gnn, False, epochs, _reload_data=reload_data,
                                                       _self_loop=_self_loop)
                            else:
                                for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                    run_one_experiment(model, task, num_gnn_layer, bench, data_shuffle,
                                                       HyperConv, _use_intermediate_gnn_results, epochs,
                                                       _reload_data=reload_data, _self_loop=_self_loop)


# send_email("train finished")


if __name__ == '__main__':
    main()
