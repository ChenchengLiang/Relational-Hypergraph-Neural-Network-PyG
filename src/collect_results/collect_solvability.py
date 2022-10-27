from utils import read_solvability_JSON
from src.utils import get_file_list


def main():
    folder = "/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/test/train_data"
    file_list = get_file_list(folder, "smt2")
    solvability_object_list = read_solvability_JSON(file_list)

    #get abstract_option_list
    abstract_option_list = []
    measurement_list = ["solvingTime", "cegarIterationNumber", "predicateGeneratorTime", "satisfiability"]
    # change getSolvability and CEGAR in Eldarica to collect generatedPredicateNumber and averagePredicateSize
    combOption = ["off", "union", "random"]
    manual_abstract_options = ["Term", "Octagon", "RelationalEqs", "RelationalIneqs"]
    predicted_abstract_options = ["predictedCG", "predictedCDHG"]
    other_abstract_options = ["Empty", "Unlabeled", "Random", "Mined"]
    cost_type = ["cost_same", "cost_shape", "cost_logit"]
    split_clause_op = ["splitClauses_1"]#"splitClauses_0"
    graph_types = ["CG", "CDHG"]
    explorationRate=[0.5]

    for sc in split_clause_op:
        for cb in combOption:
            if cb == "off":
                for ao in manual_abstract_options + other_abstract_options:  # existed templates with same cost
                    abstract_option_list.append(
                        ao + "_" + "CDHG" + "_" + cb + "_" + "0.0" + "_" + sc + "_" + "cost_same")
                for ao in predicted_abstract_options:  # predicted templates with differernt cost
                    for c in cost_type:
                        abstract_option_list.append(
                            ao + "_" + "CDHG" + "_" + cb + "_" + "0.0" + "_" + sc + "_" + c)
            elif cb == "union":
                for ao in manual_abstract_options:
                    for g in graph_types:
                        for c in cost_type:
                            abstract_option_list.append(
                                ao + "_" + g + "_" + cb + "_" + "0.0" + "_" + sc + "_" + c)
            elif cb == "random":
                for ao in manual_abstract_options:
                    for g in graph_types:
                        for c in cost_type:
                            for e in explorationRate:
                                abstract_option_list.append(
                                    ao + "_" + g + "_" + cb + "_" + str(e) + "_" + sc + "_" + c)

    #build solvability_summary_by_abstract_option
    solvability_summary_by_abstract_option={op:{"solvable_number": 0, "solvable_list": [],"solving_time_list": [],
                                                           "unique_solvable_number": 0, "unique_solvable_list": []} for op in abstract_option_list }
    print("abstract_option_list",len(solvability_summary_by_abstract_option))
    for x in solvability_summary_by_abstract_option:
        print(x,solvability_summary_by_abstract_option[x])

    # fill in solvability_summary_by_abstract_option by iterating the solvability list


if __name__ == '__main__':
    main()
