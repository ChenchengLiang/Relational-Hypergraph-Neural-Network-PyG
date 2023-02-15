from infer_utils import infer


def main():
    data_path_CDHG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CDHG"
    data_path_CG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CG"
    benchmark_dict = {data_path_CDHG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/100/9f1190ff052946c38cc4608658a39e4f/artifacts",
                      data_path_CG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/101/82713804db344ae78dc1ba10f2db9d0a/artifacts"}
    for k in benchmark_dict:
        infer(k, benchmark_dict[k])




if __name__ == '__main__':
    main()
