max_cegar_iteration = 2000
filter_out_min_solving_time = 5  # in seconds
benchmark_timeout = 60 * 20  # in seconds
data_extraction_timeout = 60 *60 *3  # in seconds
z3_solvability_folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/unsatcore-linear-z3-2955/train_data"
graph_types=["CDHG","CG"]
eldarica_abstract_options=["term","oct","relEqs","relIneqs"]
threshold_list = [0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                      0.5]