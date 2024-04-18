

## Build Environment:


We first build [Apptainer](https://apptainer.org/docs/admin/main/index.html) images (similar to docker) to serve as our environment.
Apptainer installation instructions can be found [here](https://apptainer.org/docs/admin/main/installation.html).

If you don't use containers, you can also follow the commands in .def files mentioned below to install everything.

#### 1. Eldarica container
In the folder container of this repository, build an Eldarica image by:
```
apptainer build eldarica_image.sif eldarica-compile-CEGAR-recipe.def
```
This command builds an image named eldarica_image.sif, and the recipe file is eldarica-compile-CEGAR-recipe.def.
eldarica_image.sif contains Eldarica and its dependencies.

Run this image by:
```
apptainer exec eldarica_image.sif eld -h
```
where `exec` means execute the image eldarica_image.sif, and `eld` is the command of calling Eldarica. `-h` is the parameter of Eldarica

If you see the help information from Eldarica, then you have successfully built the image.


#### 2. Python container
In the folder container of this repository, build a Python image by:
```
apptainer build python_image.sif alvis_recipe.def
```
Run this image by:
```
apptainer exec python_image.sif mlflow ui
```
Then you will see the mlflow server running in your browser 
by visiting http://127.0.0.1:5000. This server is used to receive and visualize the training results.

## Reproduce instructions:

### Task 5 reproduce instruction:






#### 1. Mine training labels [Eldarica]:
      
Ensure the problem is unsafe by running the following command:
```
apptainer exec eldarica_image.sif eld <path_to_smt2_file>
```
where <path_to_smt2_file> needs to be replaced by the path to a .smt2 file.
If Eldarica returns "unsat", then we can continue to mine labels.

We can mine the labels by the following command:
```
apptainer exec eldarica_image.sif eld <path_to_smt2_file> -mineCounterExample:common -abstract:off
```
where the parameter -mineCounterExample:common and -mineCounterExample:union denotes the two different mining strategies (i.e., (a and (b in the paper).
-abstract:off denotes we turn off manual heuristics for generating abstraction in the solving process.

Then you will get the following files in the same folder:
* a file with suffix ".simplified" which stores the simplified Horn clauses so when we read the predicted label back to Eldarica we don't simplify them again.
* a file with suffix ".counterExampleIndex.JSON" in which the field counterExampleIndices tells which clause should be labelled to 1, and others will be labelled to 0.
* a file with suffix ".log" which records the time consumption of this command 

#### 2. Draw Horn clause graphs with labels [Eldarica]: 
```
apptainer exec eldarica_image.sif eld <path_to_smt2_file> -getHornGraph:CDHG -hornGraphLabelType:unsatCore -abstract:off
```
where the parameter -getHornGraph:CDHG denotes the graph type we use in the paper, and CDHG can be replaced by CG to draw the constraint graph.
-hornGraphLabelType:unsatCore denotes the label type we use in the paper, in this case, it represents task 5.
   
Then you will get the following files in the same folder:
* a file with suffix ".hyperEdgeGraph.JSON" or "monoDirectionLayerGraph.JSON" depending the parameter -getHornGraph:CDHG or -getHornGraph:CG.
These JSON files store the graph structure and corresponding labels.


#### 3. Train and prediction [Python] 
* First we need to start a mlflow server by:
```
cd src; apptainer exec ../container/python_image.sif mlflow ui
```
This command means, go to the path under src, then run the Python image to start a mlflow server.
Notice that before we start this server, it is better to first close other mlflow servers.
This mlflow server terminal should not close while training and observing the results.

* Then we build training data folder:
In the folder benchmark/one-example-demo-unsatcore-CDHG, we have three folders: train_data, valid_data, test_data.
And, for each folder, there is a subfolder named "raw".
In each raw folder, we put our train, valid, and test data.


* Start training and prediction in a new terminal by:
```
cd src; apptainer exec ../container/python_image.sif python3 demo.py ../benchmarks/one-example-demo-unsatcore-CDHG
```
This command uses the container python_image.sif to run the python script demo.py, and the parameter "../benchmarks/one-example-demo-unsatcore-CDHG" is the path to the folder we just built.
Notice that the data folder name "one-example-demo-unsatcore-CDHG" matters, because it contains the information of the graph type (CDHG) and label type (unsatcore).

After the training, in your browser you can see the training data and prediction result in http://127.0.0.1:5000.
The training figures are included in "one-example-demo-unsatcore-CDHG/figures".

In "one-example-demo-unsatcore-CDHG/test_data/predicted", you can see the predicted labels in the file ".hyperEdgeGraph.JSON" or ".monoDirectionLayerGraph.JSON" depending the parameter -getHornGraph:CDHG or -getHornGraph:CG.

Try to replace the relative paths by absolute paths 
if there are some problems caused by the path (e.g., didn't read data in list).

#### 4. Use predicted results to guide CEGAR and SyMex [Eldarica]
```
apptainer exec eldarica_image.sif eld <path_to_smt2_file> -getSolvability -hornGraphLabelType:unsatCore -unsatCoreThreshold:0.0 -hornGraphType:CDHG -abstract:off -prioritizeClauses:constant
```
where the option constant in prioritizeClauses:constant can be replaced by label, random, score, rank, SEHPlus, SEHMinus, REHPlus, or REHMinus to apply the predicted probability in different priority functions; The CDHG in -hornGraphType:CDHG can be replaced by CG to read the predictions from the CG. In the container folder, we can build CEGAR and SyMex Eldarica images (eldarica_image.sif) by "eldarica-compile-CEGAR-recipe.def" and "eldarica-compile-CEGAR-recipe.def", respectively.

This command reads the predicted probability from ".hyperEdgeGraph.JSON" or ".monoDirectionLayerGraph.JSON" depending on the option -hornGraphType:CDHG/CG, then uses the probability in a priority function decided by the option -prioritizeClause. The solving results (i.e., SAT, UNSAT, or timeout and corresponding time consumption) are written in a .solvability.JSON file. In the file .solvability.JSON, the solving time is stored in the field "solvingTime-CDHG-0.0" when using the graph CDHG. If we use CG, then the field should be "solvingTime-CG-0.0". Similarly, the satisfiability of the .smt2 file is stored in the field "satisfiability-CDHG-0.0" where "1" and "0" represent SAT and UNSAT, respectively.
The file .solvability.JSON includes much redundant information for different options, statistics, and debugging. We suggest the users to write their own scripts to capture the solving results and corresponding time. 




## Citation
[Exploring Representation of Horn Clauses using GNNs (Extended Technical Report)](https://arxiv.org/abs/2206.06986)

```
@misc{liang2022exploring,
      title={Exploring Representation of Horn Clauses using GNNs (Extended Technical Report)}, 
      author={Chencheng Liang and Philipp Rümmer and Marc Brockschmidt},
      year={2022},
      eprint={2206.06986},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```
