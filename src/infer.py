from infer_utils import infer


def main():
    data_path_CDHG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CDHG"
    data_path_CG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CG"
    benchmark_dict = {data_path_CDHG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/44/150994ae84204326985c52d06d489d15/artifacts",
                      data_path_CG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/45/e8ce0484759644a59e60f84427fe381d/artifacts"}
    for k in benchmark_dict:
        infer(k, benchmark_dict[k])




if __name__ == '__main__':
    main()
