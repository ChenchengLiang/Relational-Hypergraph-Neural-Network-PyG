import os.path
import sys
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import get_file_list,make_dirct
from shutil import copy

def main():
    folder = sys.argv[1]
    cdhg_folder=make_dirct(folder+"-CDHG")
    cdhg_folder=make_dirct(os.path.join(cdhg_folder,"test_data"))
    cdhg_folder = make_dirct(os.path.join(cdhg_folder, "raw"))
    cg_folder=make_dirct(folder + "-CG")
    cg_folder = make_dirct(os.path.join(cg_folder, "test_data"))
    cg_folder = make_dirct(os.path.join(cg_folder, "raw"))
    for f in get_file_list(folder,"smt2"):
        file_name=f[:-len(".zip")]
        copy(f,cdhg_folder)
        copy(file_name+".simplified.zip",cdhg_folder)
        copy(file_name+".hyperEdgeGraph.JSON.zip", cdhg_folder)
        copy(file_name + ".solvability.JSON.zip", cdhg_folder)
        copy(f, cg_folder)
        copy(file_name + ".simplified.zip", cg_folder)
        copy(file_name + ".monoDirectionLayerGraph.JSON.zip", cg_folder)
        copy(file_name + ".solvability.JSON.zip", cg_folder)


if __name__ == '__main__':
    main()