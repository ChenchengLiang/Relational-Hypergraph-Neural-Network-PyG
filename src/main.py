from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from experiment_utils import run_one_experiment


def main():
    benchmarks = ["../benchmarks/unsatcore-linear-shuffled-CDHG",
                  #"../benchmarks/unsatcore_data_one-CG"
                  ]

    # load data
    # task = "unsat_core_binary_classification"
    # for _benchmark in benchmarks:
    #     run_one_experiment("hyper_GCN", task, _num_gnn_layers=2, _benchmark=_benchmark,
    #                        data_shuffle=False, _gnn=HyperConv.__name__, _use_intermediate_gnn_results=True, _epochs=1,
    #                        _reload_data=True, _self_loop=False, _add_global_edges=False, _file_name=True)

    # train
    # models = ["hyper_GCN", "GNN"]
    models = ["GNN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification","unsat_core_binary_classification"]
    tasks = ["unsat_core_binary_classification"]
    num_gnn_layers = [2]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [False]
    dropout_rate = {"gnn_dropout_rate": 0.0, "mlp_dropout_rate": 0.0, "gnn_inner_layer_dropout_rate": 0.0}
    num_linear_layer = 2
    epochs = 10
    reload_data = False
    fix_random_seed = False
    self_loop = [False]
    add_backward_edges = [False]
    add_global_edges = [True]
    use_class_weight = True  # this may interact (collapse) with gradient clip
    gradient_clip = False

    for bench in benchmarks:
        for model in models:
            for task in tasks:
                for _num_gnn_layer in num_gnn_layers:
                    for data_shuffle in data_loader_shuffle:
                        for _self_loop in self_loop:
                            if model == "GNN":
                                for _gnn in gnns:
                                    run_one_experiment(model, task, _num_gnn_layer, bench, data_shuffle,
                                                       _gnn.__name__, False, epochs, _reload_data=reload_data,
                                                       _self_loop=False, _add_backward_edges=False,
                                                       _add_global_edges=True,
                                                       _fix_random_seeds=fix_random_seed, _experiment_date=False,
                                                       _dropout_rate=dropout_rate,
                                                       _num_linear_layer=num_linear_layer,
                                                       _use_class_weight=use_class_weight, _gradient_clip=gradient_clip)
                            else:
                                for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                    for _add_backward_edge in add_backward_edges:
                                        for _add_global_edges in add_global_edges:
                                            run_one_experiment(model, task, _num_gnn_layer, bench, data_shuffle,
                                                               HyperConv.__name__, _use_intermediate_gnn_results,
                                                               epochs,
                                                               _reload_data=reload_data, _self_loop=_self_loop,
                                                               _add_backward_edges=_add_backward_edge,
                                                               _add_global_edges=_add_global_edges,
                                                               _fix_random_seeds=fix_random_seed,
                                                               _experiment_date=False,
                                                               _dropout_rate=dropout_rate,
                                                               _num_linear_layer=num_linear_layer,
                                                               _use_class_weight=use_class_weight,
                                                               _gradient_clip=gradient_clip)


# send_email("train finished")


if __name__ == '__main__':
    main()
