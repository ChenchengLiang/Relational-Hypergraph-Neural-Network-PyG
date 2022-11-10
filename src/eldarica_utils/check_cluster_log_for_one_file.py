import os
from src.utils import get_file_list
import gzip


def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-unsolvable-unlabeled-tempaltes/train_data"
    check_cluster_log_files(os.path.dirname(folder) + "/log", "out", "gz", "chc-LIA-Lin_7741.smt2")


def check_cluster_log_files(folder, file_type, compress_type, smt2_file):
    # print relation between .out and .smt2 files
    smt2_file = os.path.basename(smt2_file)
    file_list = get_file_list(folder, file_type, compress_type)
    for file in file_list:
        with gzip.open(file, 'rb') as f:
            file_content = f.read()
            file_content = file_content.decode("utf-8")
            if smt2_file in file_content:
                print("file", smt2_file)
                print("out file", file)
                print(file_content)


if __name__ == '__main__':
    main()
