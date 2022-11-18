from infer_utils import infer


def main():
    data_path_CDHG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/data/infer_test_CDHG"
    data_path_CG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/data/infer_test_CG"
    benchmark_dict = {data_path_CDHG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/18/95848ab90f9c4ead9fb1f73caa7d8351/artifacts",
                      data_path_CG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/19/5f8aee50b537467884a3a00808c726a3/artifacts"}
    for k in benchmark_dict:
        infer(k, benchmark_dict[k])




if __name__ == '__main__':
    main()
