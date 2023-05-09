import pandas as pd
from src.CONSTANTS import eldarica_abstract_options
import itertools
from src.plots import scatter_plot
from src.utils import make_dirct


def main():
    excel_file = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/statistics_split_clauses_symex--priority-queue-1000.xlsx"

    # read_gain_and_lose(excel_file)

    # sort_solvability_by_category()

    draw_common_unsafe_solving_time(excel_file)


def draw_common_unsafe_solving_time(excel_file):
    # Read the Excel file into a Pandas DataFrame
    solvability_dict = read_solvability_dict(excel_file)
    scatter_folder = make_dirct(
        "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/scatter_plots")

    comparison_pairs = [["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_SEH"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_prioritizing_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_rank"],
                        ["eldarica_abstract_off", "vb_eldarica_abstract_off_pruning_score"],
                        ["eldarica_symex_original", "vb_eldarica_symex_prioritize"],
                        #["eldarica_symex_original", "pf_eldarica_symex"]
                        ]

    axis_name_map={"eldarica_abstract_off":"Original", "vb_eldarica_abstract_off_prioritizing_SEH":"prioritizing score+",
              "vb_eldarica_abstract_off_prioritizing_rank":"Prioritizing score",
              "vb_eldarica_abstract_off_pruning_rank":"Pruning rank", "vb_eldarica_abstract_off_pruning_score":"Pruning score",
              "eldarica_symex_original":"Original", "vb_eldarica_symex_prioritize":"Prioritizing score"}
    for pair in comparison_pairs:
        if "symex" in pair[0]:
            engine= "symbolic execution"
        else:
            engine="predicate abstraction"
        original_solving_time_list = []
        strategy_solving_time_list = []
        satisfiability_list = []
        file_name_list = []
        for name, original_s, strategy_s, original_st, strategy_st in zip(solvability_dict["file_name"],
                                                                          solvability_dict[pair[0] + "_satisfiability"],
                                                                          solvability_dict[pair[1] + "_satisfiability"],
                                                                          solvability_dict[pair[0] + "_solving_time"],
                                                                          solvability_dict[pair[1] + "_solving_time"]):
            if original_s == strategy_s and original_s!="unknown":# and original_s == "unsafe":
                file_name_list.append(name)
                satisfiability_list.append(original_s)
                original_solving_time_list.append(original_st)
                strategy_solving_time_list.append(strategy_st)

        scatter_plot(x_data=original_solving_time_list, y_data=strategy_solving_time_list, z_data=satisfiability_list,
                     x_axis=axis_name_map[pair[0]], y_axis=axis_name_map[pair[1]], folder=scatter_folder, data_text=file_name_list,
                     name="Solving time (second)"+"<br>Solver engine: "+engine,scale="log")


def read_solvability_dict(excel_file):
    # Read the Excel file into a Pandas DataFrame
    df = pd.read_excel(excel_file, sheet_name='data', header=0)

    # Convert the DataFrame to a dictionary
    solvability_dict = df.to_dict(orient='list')
    return solvability_dict


def read_gain_and_lose(excel_file):
    # Read the Excel file into a Pandas DataFrame
    solvability_dict = read_solvability_dict(excel_file)

    comparison_options = ["off"] + eldarica_abstract_options

    # gain and lose number of problems
    for strategy_option in ["prioritizing_SEH", "pruning_rank"]:
        print("-" * 10 + strategy_option + "-" * 10)
        # gain problems dict
        gain_list_dict = {}
        lose_list_dict = {}
        for eldarica_option in comparison_options:
            gain_list = []
            lose_list = []
            for name, original, strategy, in zip(solvability_dict["file_name"],
                                                 solvability_dict[
                                                     "eldarica_abstract_" + eldarica_option + "_satisfiability"],
                                                 solvability_dict[
                                                     "eldarica_abstract_" + eldarica_option + "_" + strategy_option + "_satisfiability"]):
                strategy = strategy[:strategy.find("[")] if "[" in strategy else strategy
                if original == "unknown" and strategy != "unknown" and strategy != "miss info":
                    gain_list.append(name)
                if original in ["safe", "unsafe"] and strategy == "unknown":  # notice that miss info is not counted
                    lose_list.append(name)

            gain_list_dict[eldarica_option + "_gain_list"] = gain_list
            lose_list_dict[eldarica_option + "_lose_list"] = lose_list

        for k in gain_list_dict:
            print(k, len(gain_list_dict[k]))
        common_combination(gain_list_dict, comparison_options, "gain")

        print("-" * 10)

        for k in lose_list_dict:
            print(k, len(lose_list_dict[k]))
        common_combination(lose_list_dict, comparison_options, "lose")

        print("-" * 10)
        # gain and lose number for z3 and golem
        for strategy_option in ["z3", "golem"]:
            print("-" * 10)
            # gain problems dict
            gain_list_dict = {}
            lose_list_dict = {}
            gain_list = []
            lose_list = []
            for name, original, strategy, in zip(solvability_dict["file_name"],
                                                 solvability_dict[strategy_option + "_satisfiability"],
                                                 solvability_dict[strategy_option + "_pruning" + "_satisfiability"]):
                if original == "unknown" and strategy != "unknown" and strategy != "miss info":
                    gain_list.append(name)
                if original in ["safe", "unsafe"] and strategy == "unknown":  # notice that miss info is not counted
                    lose_list.append(name)

            gain_list_dict[strategy_option + "_gain_list"] = gain_list
            lose_list_dict[strategy_option + "_lose_list"] = lose_list

            for k in gain_list_dict:
                print(k, len(gain_list_dict[k]))

            print("-" * 10)

            for k in lose_list_dict:
                print(k, len(lose_list_dict[k]))


def sort_solvability_by_category():
    # find interesting numbers in category summary
    df = pd.read_excel(
        '/home/cheli243/PycharmProjects/HintsLearning/benchmarks/final-linear-evaluation/data_summary/statistics_split_clauses_1.xlsx',
        sheet_name='category_summary', header=0)

    # Convert the DataFrame to a dictionary
    category_summary_dict = df.to_dict(orient='list')
    # sort solvability
    for index, _ in enumerate(category_summary_dict["category"][:-1]):  # for each raw
        print("-" * 10)
        number_of_benchmark_in_category = category_summary_dict["vb_safe"][index] + category_summary_dict["vb_unsafe"][
            index] + category_summary_dict["vb_unknown"][index]
        print("benchmark category: ", category_summary_dict["category"][index].strip())
        print("number of problems:", number_of_benchmark_in_category)
        print("number of predicted:", category_summary_dict["number_predicted"][index])
        safe_list = []
        unsafe_list = []
        unknown_list = []
        for k in category_summary_dict:
            if "_safe" in k:
                safe_list.append((k[:k.rfind("_")], category_summary_dict[k][index]))
            if "_unsafe" in k:
                unsafe_list.append((k[:k.rfind("_")], category_summary_dict[k][index]))
            if "_unknown" in k:
                unknown_list.append((k[:k.rfind("_")], category_summary_dict[k][index]))
        safe_list = sorted(safe_list, key=lambda pair: pair[1], reverse=True)
        unsafe_list = sorted(unsafe_list, key=lambda pair: pair[1], reverse=True)
        unknown_list = sorted(unknown_list, key=lambda pair: pair[1], reverse=False)
        print("safe_list", safe_list)
        print("unsafe_list", unsafe_list)
        print("unknown_list", unknown_list)


def common_combination(data_dict, comparison_options, comparison_type):
    print("-" * 10)
    for pair in itertools.combinations(comparison_options, 2):
        common_file = set(data_dict[pair[0] + "_" + comparison_type + "_list"]).intersection(
            set(data_dict[pair[1] + "_" + comparison_type + "_list"]))
        print("common " + comparison_type + " ", pair, len(common_file))
        # different_file = set(common_list_dict[pair[0]+"_solved_unknown_list"]).difference(set(common_list_dict[pair[1]+"_solved_unknown_list"]))
        # print("different solvable ",pair,len(different_file))


if __name__ == '__main__':
    main()
