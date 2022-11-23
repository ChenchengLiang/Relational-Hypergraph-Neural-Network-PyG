import glob
import os
import sys

sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import get_file_list, compress_file


def main():
    compress_data(sys.argv[1])


def compress_data(folder):
    for f in get_file_list(folder, "smt2", ""):
        for ff in glob.glob(f + "*"):
            compress_file([ff], ff + ".zip")
            os.remove(ff)


if __name__ == '__main__':
    main()
