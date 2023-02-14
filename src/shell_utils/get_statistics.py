import sys
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.benchmark_statistics.utils import get_statistiics_in_one_folder


def main():
    get_statistiics_in_one_folder(sys.argv[1])




if __name__ == '__main__':
    main()