import sys

sys.path.append("../..")
from utils import *
from src.utils import get_file_list
from src.plots import scatter_plot
import os
import pandas as pd
from src.collect_results.utils import read_files, read_smt2_category, get_sumary_folder
from utils import get_statistiics_in_one_folder


def main():
    folder = "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/test/train_data"
    another_prioritizing_folder=folder
    z3_folder="/home/cheli243/PycharmProjects/HintsLearning/benchmarks/unsatcore-linear-z3-2955/train_data"
    get_statistiics_in_one_folder(folder,another_prioritizing_folder,z3_folder)


if __name__ == '__main__':
    main()
