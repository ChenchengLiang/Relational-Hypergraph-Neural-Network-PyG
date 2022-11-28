from infer_utils import infer


def main():
    data_path_CDHG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsat_core_infer_test-CDHG"
    data_path_CG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsat_core_infer_test-CG"
    benchmark_dict = {data_path_CDHG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/29/2984f162da5f4095af0ce8c418fe889d/artifacts",
                      data_path_CG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/30/ff391aa926164812b161df3e1776c9bb/artifacts"}
    for k in benchmark_dict:
        infer(k, benchmark_dict[k])




if __name__ == '__main__':
    main()
