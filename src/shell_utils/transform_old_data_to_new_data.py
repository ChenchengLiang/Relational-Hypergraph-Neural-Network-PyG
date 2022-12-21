from src.utils import make_dirct,get_file_list
from src.collect_results.utils import read_files
import os
def main():
    folder="/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/old-task-5-union/experiment_data"

    _change_file_names(folder)



    #change field names
    #read_files(file_list,"hyperEdgeGraph.JSON")
    #read_files(file_list, "monoDirectionLayerGraph.JSON")



def _change_file_names(folder):
    for f in get_file_list(folder,"smt2"):
        file_name=f[:-len(".zip")]
        cdhg_gv_name=file_name+".hyperEdgeHornGraph.gv.zip"
        new_cdhg_gv_name=file_name+".hyperEdgeGraph.gv.zip"
        os.rename(cdhg_gv_name,new_cdhg_gv_name)
        cdhg_json_name = file_name + ".hyperEdgeHornGraph.JSON.zip"
        new_cdhg_json_name = file_name + ".hyperEdgeGraph.JSON.zip"
        os.rename(cdhg_json_name, new_cdhg_json_name)

        cg_gv_name = file_name + ".mono-layerHornGraph.gv.zip"
        new_cg_gv_name = file_name + ".monoDirectionLayerGraph.gv.zip"
        os.rename(cg_gv_name, new_cg_gv_name)
        cg_json_name = file_name + ".mono-layerHornGraph.JSON.zip"
        new_cg_json_name = file_name + ".monoDirectionLayerGraph.JSON.zip"
        os.rename(cg_json_name, new_cg_json_name)


if __name__ == '__main__':
    main()