import os
from src.utils import get_file_list,assign_dict_key_empty_list
from utils import read_files, read_json_file,get_sumary_folder
def main():
    folder="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/unsatcore_pipeline_predicted_results"
    graph_type = {"hyperEdgeGraph": "CDHG", "monoDirectionLayerGraph": "CG"}
    threshold_list=[round(x * 0.1,2) for x in range(0, 11)]
    print(threshold_list)
    record_fields=["correctly_predicted_problem_list_"+str(x) for x in threshold_list]
    record_fields=record_fields+["file_list","correctly_predicted_problem_list"]
    statistic_dict={"CDHG":{},"CG":{}}
    assign_dict_key_empty_list(statistic_dict["CDHG"],record_fields)
    assign_dict_key_empty_list(statistic_dict["CG"], record_fields)

    #collect results
    for g in graph_type:
        graph_dict_list = read_files(get_file_list(folder, "smt2"), file_type=g+".JSON",
                                             read_function=read_json_file)
        for d in graph_dict_list:
            statistic_dict[graph_type[g]]["file_list"].append(os.path.basename(d["file_name"]))
            if d["predictedLabel"] == d["labelList"]:
                statistic_dict[graph_type[g]]["correctly_predicted_problem_list"].append(os.path.basename(d["file_name"]))

            #read predictedLabelLogit with threshold
            for threshold in threshold_list:
                predicted_label_by_logit=[1 if x>threshold else 0 for x in d["predictedLabelLogit"]]
                if predicted_label_by_logit == d["labelList"]:
                    statistic_dict[graph_type[g]]["correctly_predicted_problem_list"+"_"+str(threshold)].append(os.path.basename(d["file_name"]))

    #todo collect CEGAR ineration number


    #print results
    for g in graph_type:
        for threshold in threshold_list:
            graph_name=graph_type[g]
            correctly_predicted_number = len(statistic_dict[graph_name]["correctly_predicted_problem_list"])
            total_number=len(statistic_dict[graph_name]["file_list"])
            print(graph_name,"threshold:"+str(threshold)," correctly predicted",str(correctly_predicted_number)+"/"+ str(total_number),str((correctly_predicted_number/total_number) *100)+"%")




if __name__ == '__main__':
    main()
