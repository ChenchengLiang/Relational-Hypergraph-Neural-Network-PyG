from infer_utils import infer


def main():
    data_path_CDHG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CDHG"
    data_path_CG = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_small-infer-CG"
    benchmark_dict = {data_path_CDHG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/49/5be64c79cf41450e8cdd08c01485ebac/artifacts",
                      data_path_CG:
                          "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/src/mlruns/52/e20067aec1a1495a862f36e51289ca89/artifacts"}
    for k in benchmark_dict:
        infer(k, benchmark_dict[k])




if __name__ == '__main__':
    main()
