import sys

sys.path.append("../..")
from src.utils import make_dirct, get_file_list
import os
from extract_data_utils import run_eldarica_with_shell
from src.CONSTANTS import benchmark_timeout,threshold_list

def main():
    parameters_pipeline = []
    shell_timeout = int(benchmark_timeout)
    eldarica_timeout = benchmark_timeout
    manual_abstract_options = ["empty", "term", "oct", "relEqs", "relIneqs"]
    predicted_abstract_options = ["predictedCG", "predictedCDHG"]
    other_abstract_options = ["unlabeled", "random", "mined"]
    cost_type = ["same", "shape", "logit"]
    split_clause_option = ["1"]  # ["0","1"]
    exploration_rate = [0.5]
    data_fold = ["train_data", "valid_data", "test_data"]
    file_type = "smt2"

    # description: analysisClauses
    # parameters_pipeline.append(" -analysisClauses ")

    # description: get getSolvability # 15 hours
    # for a in manual_abstract_options:
    #     for s in split_clause_option:
    #         parameters_pipeline.append(
    #             " -getSolvability " + " -abstract:" + a + " -splitClauses:" + s + " -t:" + str(eldarica_timeout) )
    #parameters_pipeline.append(" -getSolvability " + " -abstract:off ")

    # unsatcore: get labeled data # 3 hours
    #parameters_pipeline.append(" -mineCounterExample:union -abstract:off")

    # unsatcore: construct graphs # 6 hours
    # parameters_pipeline.append(" -getHornGraph:CDHG -hornGraphLabelType:unsatCore -abstract:off")
    # parameters_pipeline.append(" -getHornGraph:CG -hornGraphLabelType:unsatCore -abstract:off")

    # unsatcore: check solvability differernt threshold #benchmark_timeout* 12*2
    #need match initial field in Eldarica and benchmark_statistics.utils in Python with threshold list
    # for g in ["CDHG", "CG"]:
    #     for threshold in threshold_list:  # reverse this list
    #         parameters_pipeline.append(" -getSolvability -hornGraphLabelType:unsatCore -unsatCoreThreshold:" + str(
    #             threshold) + " -hornGraphType:" + g +" -abstract:relEqs " )

    # unsatcore: check solvability for prioritized clauses benchmark_timeout*3
    # parameters_pipeline.append(
    #     " -getSolvability -hornGraphLabelType:unsatCore -unsatCoreThreshold:0.0 " + " -hornGraphType:CDHG -abstract:relIneqs ")
    # for g in ["CDHG", "CG"]:
    #     parameters_pipeline.append(" -getSolvability -hornGraphLabelType:unsatCore -unsatCoreThreshold:0.0 " + " -hornGraphType:" + g +" -prioritizeClausesByUnsatCoreRank -abstract:relIneqs " )

    # description: output pruned CHCs in files 12*2*shell_timeout
    shell_timeout = int(60 * 20)
    for g in ["CDHG", "CG"]:
        for threshold in threshold_list:  # reverse this list
            parameters_pipeline.append(" -outputPrunedClauses -hornGraphLabelType:unsatCore -unsatCoreThreshold:" + str(
                threshold) + " -hornGraphType:" + g + " -abstract:off ")



    # template_selection: get labeled templates # 3 hours
    # parameters_pipeline.append(" -mineTemplates -log ")

    # template_selection: for unsolvable set get unlabeled templates # 3 hours
    # parameters_pipeline.append(" -generateTemplates -abstract:unlabeled -log ")

    # template_selection: construct graphs # 6 hours
    # parameters_pipeline.append(" -getHornGraph:CDHG -hornGraphLabelType:template -log ")
    # parameters_pipeline.append(" -getHornGraph:CG -hornGraphLabelType:template -log ")

    # # template_selection: check solvability for sinlge template set # 15 hours
    # for s in split_clause_option:
    #     for ao in predicted_abstract_options + other_abstract_options:  # manual_abstract_options
    #         parameters_pipeline.append(
    #             " -getSolvability " + " -fixRandomSeed " + " -abstract:" + ao + " -splitClauses:" + s + " -t:" + str(
    #                 eldarica_timeout))
    #
    # # template_selection: check solvability for predicted template set with different cost # 12 hours
    # # unlabeled and random template set can use shape cost, but not important
    # for ao in predicted_abstract_options:
    #     for s in split_clause_option:
    #         for c in ["shape","logit"]:
    #             parameters_pipeline.append(
    #                 " -getSolvability " + " -fixRandomSeed " + " -abstract:" + ao + " -readCostType:" + c + " -splitClauses:" + s + " -t:" + str(
    #                     eldarica_timeout))
    # #
    # # template_selection: check solvability for combined predicates with two template set, union # 72 hours
    # for ao in ["term", "oct", "relEqs", "relIneqs"]:
    #     for s in split_clause_option:
    #         for g in ["CDHG","CG"]:
    #             for c in cost_type:
    #                 parameters_pipeline.append(" -getSolvability " + " -fixRandomSeed " + " -combineTemplateStrategy:union " +" -hornGraphType:"+g+
    #                                            " -abstract:" + ao + " -readCostType:" + c + " -splitClauses:" + s + " -t:" + str(eldarica_timeout))
    #
    # # template_selection: check solvability for combined predicates with two template set, random # 72 hourse
    # for ao in ["term", "oct", "relEqs", "relIneqs"]:
    #     for s in split_clause_option:
    #         for g in ["CG","CDHG"]:
    #             for c in cost_type:
    #                 for e in exploration_rate:
    #                     parameters_pipeline.append(" -getSolvability " + " -fixRandomSeed " + " -combineTemplateStrategy:random " +" -hornGraphType:"+g+
    #                                                " -abstract:" + ao + " -readCostType:" + c + " -explorationRate:"+str(e) +" -splitClauses:" + s + " -t:" + str(eldarica_timeout))

    benchmark_name = "../../benchmarks/" + sys.argv[1]
    shell_folder = os.path.join(benchmark_name, "shell_files")
    make_dirct(shell_folder)
    for eldarica_parameters in parameters_pipeline:
        for fold in data_fold:
            file_list = get_file_list(os.path.join(benchmark_name, fold), file_type)
            for file in file_list:
                run_eldarica_with_shell(file, shell_timeout, eldarica_parameters, shell_folder)


if __name__ == '__main__':
    main()
