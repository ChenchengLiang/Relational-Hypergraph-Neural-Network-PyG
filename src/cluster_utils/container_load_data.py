import sys

# sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.experiment_utils import run_one_experiment
from src.layers import HyperConv


def main():
    benchmarks = [sys.argv[1], sys.argv[2]]
    # benchmarks = [
    #     "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CDHG",
    #     "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_data_one-CG"]
    # task="template_binary_classification"
    task = "unsat_core_binary_classification"
    experiment_date = True
    # load data
    for _benchmark in benchmarks:
        run_one_experiment("hyper_GCN", task, _num_gnn_layers=2, _benchmark=_benchmark, data_shuffle=False,
                           _gnn=HyperConv.__name__, _use_intermediate_gnn_results=True, _epochs=1,
                           _reload_data=True, _fix_random_seeds=True, _experiment_date=experiment_date)


if __name__ == '__main__':
    main()
