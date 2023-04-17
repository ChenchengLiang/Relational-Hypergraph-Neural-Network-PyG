Relational-Hypergraph-Neural-Network-PyG

## Build Enviroment:

We first build an [Apptainer](https://apptainer.org/docs/admin/main/index.html) image (similar to docker) to be our environment:

Apptainer installation instructions can be find [here](https://apptainer.org/docs/admin/main/installation.html).



In folder container of this repository, build a Eldarica image by:
```
apptainer build image.sif eldarica-compile-unsatcore-recipe.def
```
Run this image by:
```
apptainer exec image.sif eld -h
```

If you see help information of Eldarica, then you have successfully built the image.



## Reproduce instructions:

[Exploring Representation of Horn Clauses using GNNs (Extended Technical Report)](https://arxiv.org/abs/2206.06986)
@misc{liang2022exploring,
      title={Exploring Representation of Horn Clauses using GNNs (Extended Technical Report)}, 
      author={Chencheng Liang and Philipp Rümmer and Marc Brockschmidt},
      year={2022},
      eprint={2206.06986},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
### Task 5 reproduce instruction:






#### 1. Mine training labels [Eldarica]:
      
Ensure the problem is unsafe by running following command:
```
apptainer exec image.sif eld <path_to_smt2_file>
```
where <path_to_smt2_file> need to be replaced to the path to a .smt2 file.
If Eldarica return "unsat", then we can continue to mine labels.

We can mine the labels by following command:
```
apptainer exec image.sif eld <path_to_smt2_file> -mineCounterExample:common -abstract:off
```
where the parameter -mineCounterExample:common and -mineCounterExample:union denotes the two different mining strategies (i.e., (a and (b in the paper).
-abstract:off denotes we turn off manual heuristics for generating abstraction in the solving process.

Then you will get following files in the same folder:
* a file with suffix ".simplified" which stores the simplified Horn clauses so when we read predicted label back to Eldarica we don't simplifiy them again.
* a file with suffix ".counterExampleIndex.JSON" in which the field counterExampleIndices tells which clause should be labelled to 1, and others will be labelled to 0.
* a file with suffix ".log" which records the time consumption of this command 

#### 2. Draw graphs with labels [Eldarica]: 
   
```
apptainer exec image.sif eld <path_to_smt2_file> -getHornGraph:CDHG -hornGraphLabelType:unsatCore -abstract:off
```
where the parameter -getHornGraph:CDHG denotes the graph type we use in the paper, and CDHG can be replaced to CG to draw constraint graph.
-hornGraphLabelType:unsatCore denotes the label type we use in the paper, in this case, it represent task 5.
   
Then you will get following files in the same folder:
* a file with suffix ".hyperEdgeGraph.JSON" or "monoDirectionLayerGraph.JSON" depending the parameter -getHornGraph:CDHG or -getHornGraph:CG.
These JSON files store the graph structure and corresponding labels.


#### 3. Train and prediction [Python] 



