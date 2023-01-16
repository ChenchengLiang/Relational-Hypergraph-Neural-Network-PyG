import sys

sys.path.append("/cephyr/users/liangch/Alvis/training_code")
from src.infer_utils import infer


def main():
    # data_path_CDHG = sys.argv[1]
    # data_path_CG = sys.argv[2]
    # model_CDHG = sys.argv[3]
    # model_CG = sys.argv[4]
    # benchmark_dict = {data_path_CDHG: model_CDHG,
    #                   data_path_CG: model_CG}
    # for k in benchmark_dict:
    #     infer(k, benchmark_dict[k])

    path=""
    model_path=""
    infer(path, model_path)


if __name__ == '__main__':
    main()
