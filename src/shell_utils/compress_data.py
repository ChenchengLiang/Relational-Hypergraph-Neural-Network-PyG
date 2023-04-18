import glob
import os
import sys

sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import compress_data


def main():
    compress_data(sys.argv[1])




if __name__ == '__main__':
    main()
