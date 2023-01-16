import sys
#sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.infer_utils import infer


def main():
    path=sys.argv[1]
    #path to artifacts
    model_path=sys.argv[2]
    infer(path, model_path)


if __name__ == '__main__':
    main()
