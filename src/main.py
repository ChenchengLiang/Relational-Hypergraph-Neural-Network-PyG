from torch_geometric.nn import GCNConv, SAGEConv, FiLMConv
from src.layers import HyperConv
from experiment_utils import run_one_experiment
from cluster_utils.utils import get_task_by_folder_name


def main():
    benchmarks = ["../benchmarks/unsatcore_pipeline_small-overfitting-CDHG",
                  "../benchmarks/unsatcore_pipeline_small-overfitting-CG",
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
    experiment_date = False
    # models = ["hyper_GCN", "GNN"]
    models = ["hyper_GCN"]
    gnns = [SAGEConv, FiLMConv, GCNConv]
    # tasks = ["argument_binary_classification","template_binary_classification","template_multi_classification","unsat_core_binary_classification"]
    task = get_task_by_folder_name(benchmarks[0])
    # todo add inner layer control to graph conv operator
    num_gnn_layers = [2, 4, 8]  # 8 works best
    dropout_rate = [  # all 0 works
        {"gnn_dropout_rate": 0.0, "mlp_dropout_rate": 0.0, "gnn_inner_layer_dropout_rate": 0.0},
        # {"gnn_dropout_rate": 0.5, "mlp_dropout_rate": 0.5, "gnn_inner_layer_dropout_rate": 0.5},
        # {"gnn_dropout_rate": 0.4, "mlp_dropout_rate": 0.2, "gnn_inner_layer_dropout_rate": 0.0},
        # {"gnn_dropout_rate": 0.8, "mlp_dropout_rate": 0.8, "gnn_inner_layer_dropout_rate": 0.0}
    ]
    num_linear_layers = [2]  # 2 works
    data_loader_shuffle = [False]
    use_intermediate_gnn_results = [False]
    message_normalization = [False]
    add_backward_edges = [False]
    add_global_edges = [True, False]
    self_loop = [True, False]
    gradient_clip = [True]
    inter_layer_norm = [True]
    embedding_size = [64]
    epochs = 200
    patient = 50
    dense_every_num_layers = 2
    residual_every_num_layers=2
    GPU = [True]
    reload_data = False
    regression_layer_norm = False
    fix_random_seed = [True]
    use_class_weight = [True]
    learning_rate = [0.001]
    activation = ["relu"]  # ["relu","leak_relu", "tanh"]
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

    parameter_dict_list = []

    for benchmark in benchmarks:
        for model in models:
            for _GPU in GPU:
                for _fix_random_seed in fix_random_seed:
                    for _use_class_weight in use_class_weight:
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
                                                                            {"model": model, "learning_task": task,
                                                                             "num_gnn_layer": num_gnn_layer,
                                                                             "experiment_name": benchmark,
                                                                             "benchmark": benchmark,
                                                                             "data_shuffle": data_shuffle,
                                                                             "gnn": gnn.__name__,
                                                                             "use_intermediate_gnn_results": False,
                                                                             "epochs": epochs, "file_name": "",
                                                                             "reload_data": True,
                                                                             "self_loop": True,
                                                                             "add_backward_edges": False,
                                                                             "add_global_edges": False,
                                                                             "fix_random_seeds": _fix_random_seed,
                                                                             "experiment_date": experiment_date,
                                                                             "dropout_rate": _dropout_rate,
                                                                             "num_linear_layer": 4,
                                                                             "use_class_weight": _use_class_weight,
                                                                             "gradient_clip": _gradient_clip,
                                                                             "add_global_edges": _add_global_edge,
                                                                             "learning_rate": _learning_rate,
                                                                             "activation": _activation,
                                                                             "cdhg_edge_types": cdhg_edge_types,
                                                                             "cg_edge_types": cg_edge_types,
                                                                             "embedding_size": _embedding_size,
                                                                             "GPU": _GPU,
                                                                             "regression_layer_norm": regression_layer_norm,
                                                                             "patient": patient,
                                                                             "dense_every_num_layers": dense_every_num_layers,"residual_every_num_layers":residual_every_num_layers})


                                                                else:
                                                                    for _use_intermediate_gnn_results in use_intermediate_gnn_results:
                                                                        for _add_backward_edge in add_backward_edges:
                                                                            for _message_normalization in message_normalization:
                                                                                for _inter_layer_norm in inter_layer_norm:
                                                                                    parameter_dict_list.append(
                                                                                        {"model": model,
                                                                                         "learning_task": task,
                                                                                         "num_gnn_layer": num_gnn_layer,
                                                                                         "experiment_name": benchmark,
                                                                                         "benchmark": benchmark,
                                                                                         "data_shuffle": data_shuffle,
                                                                                         "gnn": HyperConv.__name__,
                                                                                         "use_intermediate_gnn_results": _use_intermediate_gnn_results,
                                                                                         "epochs": epochs,
                                                                                         "file_name": "",
                                                                                         "reload_data": reload_data,
                                                                                         "self_loop": _self_loop,
                                                                                         "add_backward_edges": _add_backward_edge,
                                                                                         "add_global_edges": _add_global_edge,
                                                                                         "fix_random_seeds": _fix_random_seed,
                                                                                         "experiment_date": experiment_date,
                                                                                         "dropout_rate": _dropout_rate,
                                                                                         "num_linear_layer": num_linear_layer,
                                                                                         "use_class_weight": _use_class_weight,
                                                                                         "gradient_clip": _gradient_clip,
                                                                                         "learning_rate": _learning_rate,
                                                                                         "activation": _activation,
                                                                                         "cdhg_edge_types": cdhg_edge_types,
                                                                                         "cg_edge_types": cg_edge_types,
                                                                                         "embedding_size": _embedding_size,
                                                                                         "message_normalization": _message_normalization,
                                                                                         "inter_layer_norm": _inter_layer_norm,
                                                                                         "GPU": _GPU,
                                                                                         "regression_layer_norm": regression_layer_norm,
                                                                                         "patient": patient,
                                                                                         "dense_every_num_layers": dense_every_num_layers,"residual_every_num_layers":residual_every_num_layers})
    for i, parameter_dict in enumerate(parameter_dict_list):
        run_one_experiment(parameter_dict)


if __name__ == '__main__':
    main()
