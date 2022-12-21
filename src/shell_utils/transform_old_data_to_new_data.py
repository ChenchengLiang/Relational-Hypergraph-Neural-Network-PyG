import sys
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.utils import make_dirct, get_file_list, common_files,compress_file,unzip_file
from src.collect_results.utils import read_files,read_json_file
import os
import json


def main():
    folder = sys.argv[1]
    _change_file_names(folder)

    # change field names
    cdhg_field_map = {"nodeIds": "nodeIDList", "nodeSymbolList": "nodeSymbolList", "guardIndices": "labelIndices",
                       "clauseBinaryOccurrenceInCounterExampleList": "labelList",
                       "argumentEdges": "relationSymbolArgumentEdge",
                       "guardASTEdges": "guardEdge", "AST_1Edges": "ASTLeftEdge", "AST_2Edges": "ASTRightEdge",
                       "ASTEdges": "ASTEdge", "controlFlowHyperEdges": "controlFlowHyperEdge",
                       "dataFlowHyperEdges": "dataFlowHyperEdge"}

    cg_field_map = {"nodeIds": "nodeIDList", "nodeSymbolList": "nodeSymbolList", "clauseIndices": "labelIndices",
                     "clauseBinaryOccurrenceInCounterExampleList": "labelList", "predicateArgumentEdges": "relationSymbolArgumentEdge",
                     "predicateInstanceEdges": "relationSymbolInstanceEdge", "argumentInstanceEdges":"argumentInstanceEdge",
                     "controlHeadEdges": "clauseHeadEdge", "controlBodyEdges": "clauseBodyEdge", "controlArgumentEdges": "clauseArgumentEdge",
                     "subTermEdges": "ASTEdge", "guardEdges": "guardEdge", "dataEdges": "dataEdge"}

    for graph_type,field_map in zip(["hyperEdgeGraph.JSON","monoDirectionLayerGraph.JSON"],[cdhg_field_map,cg_field_map]):
        file_list=get_file_list(folder,"smt2")
        for obj in read_files(file_list,graph_type,read_json_file):
            new_obj={"quantifierEdge":[[0,0]],"ASTLeftEdge":[[0,0]],"ASTRightEdge":[[0,0]]}
            for filed in field_map:
                new_obj[field_map[filed]]=obj[filed]
            #write new object to json
            json_file_name=obj["file_name"]+"."+graph_type
            with open(json_file_name, "w") as f:
                json.dump(new_obj, f)
            os.remove(json_file_name+".zip")
            compress_file([json_file_name],json_file_name+".zip")
            os.remove(json_file_name)




def _change_file_names(folder):
    for f in get_file_list(folder, "smt2"):
        file_name = f[:-len(".zip")]

        cdhg_gv_name = file_name + ".hyperEdgeHornGraph.gv.zip"
        cdhg_gv_name_new=file_name + ".hyperEdgeGraph.gv"
        unzip_file(cdhg_gv_name)
        os.remove(cdhg_gv_name)
        os.rename(file_name + ".hyperEdgeHornGraph.gv",cdhg_gv_name_new)
        compress_file([cdhg_gv_name_new],cdhg_gv_name_new+".zip")
        os.remove(cdhg_gv_name_new)

        cdhg_json_name = file_name + ".hyperEdgeHornGraph.JSON.zip"
        cdhg_json_name_new=file_name + ".hyperEdgeGraph.JSON"
        unzip_file(cdhg_json_name)
        os.remove(cdhg_json_name)
        os.rename(file_name + ".hyperEdgeHornGraph.JSON", cdhg_json_name_new)
        compress_file([cdhg_json_name_new], cdhg_json_name_new+".zip")
        os.remove(cdhg_json_name_new)

        cg_gv_name = file_name + ".mono-layerHornGraph.gv.zip"
        cg_gv_name_new=file_name + ".monoDirectionLayerGraph.gv"
        unzip_file(cg_gv_name)
        os.remove(cg_gv_name)
        os.rename(file_name + ".mono-layerHornGraph.gv", cg_gv_name_new)
        compress_file([cg_gv_name_new], cg_gv_name_new+".zip")
        os.remove(cg_gv_name_new)

        cg_json_name = file_name + ".mono-layerHornGraph.JSON.zip"
        cg_json_name_new=file_name + ".monoDirectionLayerGraph.JSON"
        unzip_file(cg_json_name)
        os.remove(cg_json_name)
        os.rename(file_name + ".mono-layerHornGraph.JSON", cg_json_name_new)
        compress_file([cg_json_name_new], cg_json_name_new + ".zip")
        os.remove(cg_json_name_new)





if __name__ == '__main__':
    main()
