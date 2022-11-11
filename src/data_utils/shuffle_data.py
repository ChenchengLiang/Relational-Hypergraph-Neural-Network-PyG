import os
from src.collect_results.utils import copy_relative_files
from src.utils import get_file_list,make_dirct
import random
import os

def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/uppmax-non-linear-graphs/4-ready-for-training"
    file_list = get_file_list(folder, "smt2")
    file_list_number=len(file_list)
    random.seed(42)
    for i in range(5):
        random.shuffle(file_list)

    train_fold, valid_fold, test_fold = 0.8, 0.1, 0.1
    train_files = file_list[0:int(file_list_number * train_fold)]
    valid_files = file_list[int(file_list_number * train_fold):int(file_list_number * (1 - valid_fold))]
    test_files = file_list[int(file_list_number * (1 - test_fold)):file_list_number]

    shuffled_folder=make_dirct(folder +  "-shuffled")

    for fold_file_list,fold in zip([train_files,valid_files,test_files],["train_data","valid_data","test_data"]):
        copy_files_to_folds(shuffled_folder,fold_file_list,fold)

def copy_files_to_folds(shuffled_folder,fold_file_list,fold):
    shuffled_folder_train = make_dirct(os.path.join(shuffled_folder, fold))
    shuffled_folder_train_raw = make_dirct(os.path.join(shuffled_folder_train, "raw"))
    for file in fold_file_list:
        file=file[:-len(".zip")]
        copy_relative_files(file,shuffled_folder_train_raw)

if __name__ == '__main__':
    main()
