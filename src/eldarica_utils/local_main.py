from check_extracted_data_from_cluster import separate_corner_cases_from_cluster_graph_construction, \
    separate_corner_cases_from_cluster_mineTemplates


def main():
    # for solvability
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-solvability",
    #     file_numebr=3, target_message="ready_for_template_mining", source="check-solvability")
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-solvability",
    #     file_numebr=3, target_message="ready_for_template_mining", source="check-solvability")
    # for mined templates
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-mined-template",
    #     file_numebr=7, target_message="ready_for_graph_construction", source="mine-tempaltes")
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-mined-template",
    #     file_numebr=7, target_message="ready_for_graph_construction", source="mine-tempaltes")

    # for unsolvable unlabeled templates
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-unsolvable-unlabeled-tempaltes",
    #     file_numebr=4, target_message="ready_for_graph_construction",source="generate-unlabeled-tempaltes")
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-unsolvable-unlabeled-tempaltes",
    #     file_numebr=4, target_message="ready_for_graph_construction", source="generate-unlabeled-tempaltes")

    #for no-simplified clause solvability
    # separate_corner_cases_from_cluster_mineTemplates(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-no-simplified-clauses-solvability-1697.zip",
    #     file_numebr=3, target_message="ready_for_template_mining", source="check-solvability")

    #for unsat problem solvability
    separate_corner_cases_from_cluster_mineTemplates(
        folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-unsat-divided-2160",
        file_numebr=3, target_message="ready_for_counter_example_mining", source="check-solvability")
    separate_corner_cases_from_cluster_mineTemplates(
        folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-unsat-divided-3668",
        file_numebr=3, target_message="ready_for_counter_example_mining", source="check-solvability")





    # for constructed graphs
    # separate_corner_cases_from_cluster_graph_construction(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Template-selection-Liner-dateset-new/splitClause1/3-uppmax-linear-graphs",
    #     file_numebr=11, target_message="not-timeout-cases", source="construct-graphs")
    # separate_corner_cases_from_cluster_graph_construction(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-graphs",
    #     file_numebr=11, target_message="not-timeout-cases",source="construct-graphs")

    # for unsolvable constructed graphs
    # separate_corner_cases_from_cluster_graph_construction(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-unsolvable-graphs",
    #     file_numebr=8, target_message="not-timeout-cases", source="construct-graphs")
    # separate_corner_cases_from_cluster_graph_construction(
    #     folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-linear-unsolvable-graphs",
    #     file_numebr=6, target_message="not-timeout-cases", source="construct-graphs")



if __name__ == '__main__':
    main()
