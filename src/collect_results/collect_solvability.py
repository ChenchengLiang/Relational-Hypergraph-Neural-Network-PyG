from utils import read_solvability_JSON
from src.utils import get_file_list
def main():
    folder="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/test/train_data"
    file_list = get_file_list(folder,"smt2")
    solvability_object_list=read_solvability_JSON(file_list)

    # solvability_summary_by_abstract_option = {
    #     op: {"solvable_number": 0, "solvable_list": [], "solving_time_list": [],
    #     "unique_solvable_number": 0, "unique_solvable_list": []} for op
    #     in abstract_option}
    solvability_summary_by_abstract_option = {}












if __name__ == '__main__':
    main()