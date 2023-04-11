import pandas as pd
from src.CONSTANTS import eldarica_abstract_options
import itertools


def main():
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(
        '/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/statistics_split_clauses_1.xlsx',
        sheet_name='data', header=0)

    # Convert the DataFrame to a dictionary
    solvability_dict = df.to_dict(orient='list')



    comparison_options = ["off"] + eldarica_abstract_options

    # gain and lose number of problems
    for strategy_option in ["prioritizing_SEH", "pruning_rank"]:
        print("-"*10)
        # gain problems dict
        gain_list_dict = {}
        for eldarica_option in comparison_options:
            gain_list = []
            for name, original, strategy, in zip(solvability_dict["file_name"],
                                                       solvability_dict["eldarica_abstract_" + eldarica_option + "_satisfiability"],
                                                       solvability_dict[
                                                           "eldarica_abstract_" + eldarica_option + "_"+strategy_option+"_satisfiability"]):
                strategy= strategy[:strategy.find("[")] if "[" in strategy else strategy
                if original == "unknown" and strategy != "unknown" and strategy != "miss info":
                    gain_list.append(name)
            gain_list_dict[eldarica_option + "_gain_list"] = gain_list
            print(eldarica_option + " gains by "+strategy_option+" ", len(gain_list))

        common_combination(gain_list_dict, comparison_options, "gain")



        print("-" * 10)

        # lose problems dict
        lose_list_dict = {}
        for eldarica_option in comparison_options:
            lose_list = []
            for name, original, strategy, in zip(solvability_dict["file_name"],
                                                       solvability_dict["eldarica_abstract_" + eldarica_option + "_satisfiability"],
                                                       solvability_dict[
                                                           "eldarica_abstract_" + eldarica_option + "_"+strategy_option+"_satisfiability"]):
                strategy = strategy[:strategy.find("[")] if "[" in strategy else strategy
                if original != "unknown" and strategy == "unknown":  # notice that miss info is not counted
                    lose_list.append(name)
            lose_list_dict[eldarica_option + "_lose_list"] = lose_list
            print(eldarica_option + " loses by "+strategy_option+" ", len(lose_list))


        common_combination(lose_list_dict,comparison_options,"lose")


    #todo find interesting numbers in category summary



def common_combination(data_dict,comparison_options,comparison_type):
    print("-" * 10)
    for pair in itertools.combinations(comparison_options, 2):
        common_file = set(data_dict[pair[0] + "_"+comparison_type+"_list"]).intersection(
            set(data_dict[pair[1] + "_"+comparison_type+"_list"]))
        print("common "+comparison_type+" ", pair, len(common_file))
        # different_file = set(common_list_dict[pair[0]+"_solved_unknown_list"]).difference(set(common_list_dict[pair[1]+"_solved_unknown_list"]))
        # print("different solvable ",pair,len(different_file))

if __name__ == '__main__':
    main()
