import os.path
import sys

sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.collect_results.utils import copy_relative_files
from src.utils import get_file_list, make_dirct
from shutil import copy


def main():
    folder = sys.argv[1]
    n = int(sys.argv[2])
    file_list = get_file_list(folder, "smt2")
    divided_list = divide_list(file_list, n)

    for i, l in enumerate(divided_list):
        current_folder_CDHG = make_dirct(folder + "-part-" + str(i)+"-CDHG")
        current_folder_CDHG = make_dirct(os.path.join(current_folder_CDHG,"test_data"))
        current_folder_CDHG = make_dirct(os.path.join(current_folder_CDHG, "raw"))
        current_folder_CG = make_dirct(folder + "-part-" + str(i) + "-CG")
        current_folder_CG = make_dirct(os.path.join(current_folder_CG, "test_data"))
        current_folder_CG = make_dirct(os.path.join(current_folder_CG, "raw"))
        for f in l:
            copy_relative_files(f[:-len(".zip")], current_folder_CDHG)
            copy_relative_files(f[:-len(".zip")], current_folder_CG)


def divide_list(lst, n):
    """Divide a list into n roughly equal parts."""
    division = len(lst) / n
    return [lst[round(division * i):round(division * (i + 1))] for i in range(n)]


if __name__ == '__main__':
    main()
