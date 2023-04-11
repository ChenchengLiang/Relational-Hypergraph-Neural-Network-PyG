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

    comparison_options=eldarica_abstract_options + ["off"]
    # new solved problems dict
    gain_list_dict = {}
    for option in comparison_options:
        gain_list = []
        for name, original, prioritize_SEH, in zip(solvability_dict["file_name"],
                                              solvability_dict["eldarica_abstract_" + option + "_satisfiability"],
                                              solvability_dict[
                                                  "vb_eldarica_abstract_" + option + "_prioritizing_SEH_satisfiability"]):
            if original == "unknown" and prioritize_SEH != "unknown":
                gain_list.append(name)
        gain_list_dict[option + "_gain_list"] = gain_list
        print(option + " gains by prioritizing_SEH ", len(gain_list))



    print("-" * 10)
    # print number of common gains and loses

    for pair in itertools.combinations(comparison_options, 2):
        common_file = set(gain_list_dict[pair[0] + "_gain_list"]).intersection(
            set(gain_list_dict[pair[1] + "_gain_list"]))
        print("common gains ", pair, len(common_file))
        # different_file = set(common_list_dict[pair[0]+"_solved_unknown_list"]).difference(set(common_list_dict[pair[1]+"_solved_unknown_list"]))
        # print("different solvable ",pair,len(different_file))

    print("-" * 10)


    lose_list_dict = {}
    for option in comparison_options:
        lose_list = []
        for name, original, prioritize_SEH, in zip(solvability_dict["file_name"],
                                              solvability_dict["eldarica_abstract_" + option + "_satisfiability"],
                                              solvability_dict[
                                                  "eldarica_abstract_" + option + "_prioritizing_SEH_satisfiability"]):
            if original != "unknown" and prioritize_SEH == "unknown":  # notice that miss info is not counted
                lose_list.append(name)
        lose_list_dict[option + "_lose_list"] = lose_list
        print(option + " loses by prioritizing_SEH ", len(lose_list))

    print("-" * 10)

    for pair in itertools.combinations(comparison_options, 2):
        common_file = set(lose_list_dict[pair[0] + "_lose_list"]).intersection(
            set(lose_list_dict[pair[1] + "_lose_list"]))
        print("common lose ", pair, len(common_file))




if __name__ == '__main__':
    main()
