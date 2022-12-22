from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from experiment_utils import run_one_experiment
from cluster_utils.utils import get_task_by_folder_name

def main():
    benchmarks = ["../benchmarks/unsatcore-old-data-union-CDHG",
                  "../benchmarks/unsatcore-old-data-union-CG",
                  "../benchmarks/unsatcore-old-data-common-CDHG",
                  "../benchmarks/unsatcore-old-data-common-CG"
                  ]

    # load data
    # task = get_task_by_folder_name(benchmarks[0])
    # for _benchmark in benchmarks:
    #     run_one_experiment("hyper_GCN", task, _num_gnn_layers=2, _benchmark=_benchmark,
    #                        data_shuffle=False, _gnn=HyperConv.__name__, _use_intermediate_gnn_results=False, _epochs=1,
    #                        _reload_data=True, _self_loop=False, _add_global_edges=False,_add_backward_edges=False,
    #                        _file_name="",_experiment_name="load_data")

    # train
    _train(benchmarks)


# send_email("train finished")

def _train(benchmarks):
    # models = ["hyper_GCN", "GNN"]
    models = ["hyper_GCN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification","unsatcore_binary_classification"]
    task = get_task_by_folder_name(benchmarks[0])
    num_gnn_layers = [4]
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [True]
    dropout_rate = {"gnn_dropout_rate": 0.0, "mlp_dropout_rate": 0.0, "gnn_inner_layer_dropout_rate": 0.0}
    num_linear_layer = 4
    epochs = 300
    reload_data = False
    fix_random_seed = False
    self_loop = [False]
    add_backward_edges = [False]
    add_global_edges = [True]
    use_class_weight = True  # this may interact (collapse) with gradient clip
    gradient_clip = False
    cdhg_edge_types = ["relationSymbolArgumentEdge", "guardEdge",
                       "ASTLeftEdge", "ASTRightEdge",
                       # "ASTEdge",
                       # "quantifierEdge",
                       "controlFlowHyperEdge", "dataFlowHyperEdge"]
    cg_edge_types = ["relationSymbolArgumentEdge", "relationSymbolInstanceEdge", "argumentInstanceEdge",
                     "clauseHeadEdge", "clauseBodyEdge", "clauseArgumentEdge",
                     # "ASTLeftEdge", "ASTRightEdge",
                     "ASTEdge",
                     # "quantifierEdge",
                     "guardEdge", "dataEdge",
                     ]

    for bench in benchmarks:
        for model in models:
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
                                                   _use_class_weight=use_class_weight, _gradient_clip=gradient_clip,
                                                   _cdhg_edge_types=cdhg_edge_types, _cg_edge_types=cg_edge_types)
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
                                                           _gradient_clip=gradient_clip,
                                                           _cdhg_edge_types=cdhg_edge_types,
                                                           _cg_edge_types=cg_edge_types)
if __name__ == '__main__':
    main()
