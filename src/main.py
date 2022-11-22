from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from experiment_utils import run_one_experiment


def main():
    benchmarks = ["../data/overfitted-train-shuffled-CDHG","../data/overfitted-train-shuffled-CG"]
    _self_loop = False

    # load data
    for _benchmark in benchmarks:
        run_one_experiment("hyper_GCN", "template_binary_classification", _num_gnn_layers=2, _benchmark=_benchmark,
                           data_shuffle=False, _gnn=HyperConv, _use_intermediate_gnn_results=True, _epochs=1,
                           _reload_data=True, _self_loop=_self_loop, _file_name=True)

    # train
    models = ["hyper_GCN", "GNN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification"]
    tasks = ["template_binary_classification"]
    num_gnn_layers = [2, 4, 8]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [True, False]
    epochs = 2
    reload_data = False
    fix_random_seed = True

    for bench in benchmarks:
        for model in models:
            for task in tasks:
                for _num_gnn_layer in num_gnn_layers:
                    for data_shuffle in data_loader_shuffle:

                        if model == "GNN":
                            for _gnn in gnns:
                                run_one_experiment(model, task, _num_gnn_layer, bench, data_shuffle,
                                                   _gnn, False, epochs, _reload_data=reload_data,
                                                   _self_loop=_self_loop, _file_name=fix_random_seed)
                        else:
                            for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                run_one_experiment(model, task, _num_gnn_layer, bench, data_shuffle,
                                                   HyperConv, _use_intermediate_gnn_results, epochs,
                                                   _reload_data=reload_data, _self_loop=_self_loop,
                                                   _file_name=fix_random_seed)


# send_email("train finished")


if __name__ == '__main__':
    main()
