import sys

# sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.experiment_utils import run_one_experiment
from src.layers import HyperConv
from utils import get_task_by_folder_name

def main():
    folder_name = sys.argv[1]
    benchmarks = [folder_name]
    task= get_task_by_folder_name(folder_name)

    experiment_date = True
    # load data
    for _benchmark in benchmarks:
        run_one_experiment("hyper_GCN", task, _num_gnn_layers=2, _benchmark=_benchmark, data_shuffle=False,
                           _gnn=HyperConv.__name__, _use_intermediate_gnn_results=True, _epochs=1,
                           _reload_data=True, _fix_random_seeds=True, _experiment_date=experiment_date,
                           _experiment_name="load_data")


if __name__ == '__main__':
    main()
