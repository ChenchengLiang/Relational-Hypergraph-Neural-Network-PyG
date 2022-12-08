import sys

sys.path.append("../..")
import pandas as pd
from utils import get_category_summary, get_statistic_summary


def main():
    # read excel
    xls = pd.ExcelFile(
        '/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-backup.xlsx')
    linear_data = pd.read_excel(xls, 'linear')
    non_linear_data = pd.read_excel(xls, 'non-linear')
    print(linear_data.keys())

    linear_category_summary = get_category_summary(linear_data)
    non_linear_category_summary = get_category_summary(non_linear_data)

    linear_summary = get_statistic_summary(linear_data)
    non_linear_summary = get_statistic_summary(non_linear_data)

    # write to excel

    with pd.ExcelWriter(
            "/home/cheli243/PycharmProjects/HintsLearning/benchmarks/benchmark_statistics_split_clauses_1-summary.xlsx") as writer:
        linear_data.pop("Unnamed: 0")
        pd.DataFrame(pd.DataFrame(linear_data)).to_excel(writer, sheet_name="linear")
        non_linear_data.pop("Unnamed: 0")
        pd.DataFrame(pd.DataFrame(non_linear_data)).to_excel(writer, sheet_name="non_linear")
        pd.DataFrame(pd.DataFrame(linear_summary)).to_excel(writer, sheet_name="linear_summary")
        pd.DataFrame(pd.DataFrame(non_linear_summary)).to_excel(writer, sheet_name="non_linear_summary")
        pd.DataFrame(pd.DataFrame(linear_category_summary)).to_excel(writer, sheet_name="linear_category_summary")
        pd.DataFrame(pd.DataFrame(non_linear_category_summary)).to_excel(writer,
                                                                         sheet_name="non_linear_category_summary")


if __name__ == '__main__':
    main()
