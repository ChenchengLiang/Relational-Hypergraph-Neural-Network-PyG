import sys
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import get_file_list, make_dirct
from src.collect_results.utils import copy_relative_files
from os.path import join as opj
import shutil


def main():
    divide_threads(sys.argv[1])

def divide_threads(folder):
    file_list=get_file_list(folder,"smt2")
    divided_folder=make_dirct(folder+"-divided-"+str(len(file_list)))
    for i,file in enumerate(file_list):
        file_name=file[:-len(".zip")]
        thread_folder=make_dirct(opj(divided_folder,"thread_"+str(i)))
        target_folder = make_dirct(opj(thread_folder,"train_data"))
        copy_relative_files(file_name,target_folder)

    shutil.make_archive(divided_folder, 'zip', divided_folder)
    shutil.rmtree(divided_folder)


if __name__ == '__main__':
    main()