import os

from src.utils import get_file_list
from src.collect_results.utils import read_files,read_json_file
def main():
    index_folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/temp_index"
    #todo: check the statistics
    source_folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/temp_source"
    #/home/cheli243/PycharmProjects/HintsLearning/benchmarks/Linear-dateset-new/splitClauses-1/simplfied-clauses
    index_file_list=get_file_list(index_folder,"smt2")

    target_file_list=[]
    for json_obj in read_files(index_file_list, file_type="solvability.JSON", read_function=read_json_file):
        if len(json_obj) > 1:  # has solvability file
            if json_obj["clauseNumberAfterSimplification"]>json_obj["clauseNumberBeforeSimplification"]:
                file_name=os.path.basename(json_obj["file_name"])
                target_file_list.append(file_name)

    print(target_file_list)

    for f in target_file_list:
        pass





if __name__ == '__main__':
    main()