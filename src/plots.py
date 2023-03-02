import os
import sys

sys.path.append("../..")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import mlflow
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix
import plotly.express as px
import plotly.io as pio
import numpy as np
from src.utils import count_generator, make_dirct

plt.style.use("ggplot")


def scatter_plot(x_data, y_data, z_data, x_axis, y_axis, folder, data_text, name):
    fig = go.Figure()
    if len(z_data) != 0:
        x_data_1, y_data_1, text_data_1, x_data_2, y_data_2, text_data_2, x_data_3, y_data_3, text_data_3 = [], [], [], [], [], [], [], [], []
        for x, y, z, t in zip(x_data, y_data, z_data, data_text):
            if z == "safe":  # z != 10800:
                x_data_1.append(x)
                y_data_1.append(y)
                text_data_1.append(t)
            elif z == "unsafe":
                x_data_2.append(x)
                y_data_2.append(y)
                text_data_2.append(t)
            else:
                x_data_3.append(x)
                y_data_3.append(y)
                text_data_3.append(t)
        fig.add_trace(go.Scatter(x=x_data_1, y=y_data_1, text=text_data_1, marker=dict(color='green'), mode='markers',
                                 name='safe'))
        fig.add_trace(go.Scatter(x=x_data_2, y=y_data_2, text=text_data_2, marker=dict(color='blue', symbol="diamond"),
                                 mode='markers',
                                 name='unsafe'))  # size=10
        fig.add_trace(
            go.Scatter(x=x_data_3, y=y_data_3, text=text_data_3, marker=dict(color='red', symbol="x"), mode='markers',
                       name='unknown'))
    else:
        fig.add_trace(go.Scatter(x=x_data, y=y_data, marker=dict(color='blue'), mode='markers', name='marker'))

    # Add a diagonal line
    max_value = max(x_data + y_data)
    fig.add_trace(
        go.Scatter(x=[0, max_value], y=[0, max_value], mode="lines", name="diagonal", line=dict(color="gray")))

    fig.update_layout(
        title=name,
        title_x=0.5,
        title_y=0.5,
        xaxis_title=x_axis,
        yaxis_title=y_axis)
    plot_file_name = name + "-" + x_axis + "-vs-" + y_axis
    save_file_name = os.path.join(folder, plot_file_name)
    # fig.update_yaxes(type="linear")
    fig.write_html(save_file_name + ".html")
    fig.write_image(save_file_name + ".png")


def train_valid_plot(train_loss_floats, valid_loss_floats, folder, field="loss"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(train_loss_floats))),
        y=train_loss_floats,
        name="train_" + field
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(valid_loss_floats))),
        y=valid_loss_floats,
        name="valid_" + field
    ))

    fig.update_layout(
        title='',
        xaxis_title='epochs',
        yaxis_title=field)
    plot_name = field
    figure_folder = make_dirct(os.path.join(folder, "figures"))
    save_file_name = os.path.join(figure_folder, plot_name + ".html")
    # fig.update_yaxes(type="linear")
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)


def count_element_in_generator(e, generator):
    counter = 0
    for i in generator():
        if e == i:
            counter += 1
    return counter


def draw_label_pie_chart(num_label, learning_label_generator, folder, name=""):
    label_name_list = list(range(num_label))
    flat_list_generator = lambda: (item for sublist in learning_label_generator() for item in sublist)
    values = [count_element_in_generator(i, flat_list_generator) for i in label_name_list]
    pull = [0.2 if v / sum(values) < 0.01 else 0 for v in values]  # if percentage < 0.01, pull it out from the pie
    fig = go.Figure(data=[go.Pie(labels=label_name_list, values=values, pull=pull)])
    fig.update_layout(title=name + "-" + str(count_generator(learning_label_generator())))
    figure_folder = make_dirct(os.path.join(folder, "figures"))
    save_file_name = os.path.join(figure_folder, name + "-distribution.html")
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)
    mlflow.set_tag(name + " dominate distribution", max(values) / sum(values))
    return values


def draw_confusion_matrix(predicted_y, true_y, num_classes, folder, name="", acc=""):
    label_list = list(range(num_classes))
    cm = confusion_matrix(true_y, predicted_y, labels=label_list)
    fig = px.imshow(cm, x=label_list, y=label_list, text_auto=True)
    fig.update_layout(
        title='confusion matrix, ' + "accuracy: " + str(acc),
        xaxis_title='predicted_y',
        yaxis_title='true_y')
    figure_folder = make_dirct(os.path.join(folder, "figures"))
    save_file_name = os.path.join(figure_folder, name + "-confusion-matrix.html")
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)


def plot_cactus(summary_folder, solvability_summary, plot_name=""):
    # solvability_summary={solving_option_1:{solving_time_list:[],"cegar_iteration_number_list:[],...},solving_option_2:{solving_time_list:[],"cegar_iteration_number_list:[],...}}
    max_time = np.max(np.max(np.array([item["solvingTime_list"] for item in solvability_summary.values()]))) / 1000
    print("max_time s", max_time)
    cactus = {}
    time_limit = int(max_time) + 2
    for option in solvability_summary:
        cactus[option] = [0]
        solved_index = 0
        for t in range(0, time_limit):
            solved_counter = 0
            for st in solvability_summary[option]["solvingTime_list"]:
                if st / 1000 < t:
                    solved_counter = solved_counter + 1
                if solved_counter > solved_index:
                    cactus[option].append(t)
                    solved_index = solved_counter

    # key_words=["Term","Octagon","RelationalEqs","RelationalIneqs"]
    # for k in key_words:
    #     draw_one_cactus_plotly(summary_folder,cactus,k)

    # draw_one_cactus(summary_folder, cactus, "")
    draw_one_cactus_plotly(summary_folder, cactus, key_word="", scale="linear", plot_name=plot_name)
    draw_one_cactus_plotly(summary_folder, cactus, key_word="", scale="log", plot_name=plot_name)


def draw_one_cactus_plotly(summary_folder, cactus, key_word, scale="", plot_name=""):
    # sort lines by solved problems for the highest time limit
    key_word_map_to_legend = {"prioritizeClausesByUnsatCoreRank-CG-score with existed heuristics": "CG-SEH",
                              "prioritizeClausesByUnsatCoreRank-CG-only score": "CG-score",
                              "prioritizeClausesByUnsatCoreRank-CDHG-score with existed heuristics": "CDHG-SEH",
                              "prioritizeClausesByUnsatCoreRank-CDHG-only score": "CDHG-score"}
    lines = []
    for k in cactus:
        cactus_without_zero = [0] + [x for x in cactus[k] if x != 0]
        if key_word in k:
            if k in key_word_map_to_legend.keys():
                lines.append((len(cactus[k]), key_word_map_to_legend[k], cactus_without_zero))
            else:
                lines.append((len(cactus[k]), k, cactus_without_zero))
    lines.sort(reverse=True)

    fig = go.Figure()
    for line in lines:
        # print(line[0],line[1],line[2])
        if key_word in line[1]:
            fig.add_trace(go.Scatter(
                x=list(range(len(line[2]))),
                y=line[2],
                name=line[1]  # , mode='lines+markers'
            ))

    fig.update_layout(  # legend_title_text='Trend',
        title='',
        height=700,
        width=800,
        autosize=True,
        xaxis_title='Solved benchmarks',
        yaxis_title='Time limit (s)')
    fig.update_yaxes(type=scale)
    fig.write_html(summary_folder + "/" + plot_name + key_word + "-" + scale + "-cactus.html")
    fig.write_image(summary_folder + "/" + plot_name + key_word + "-" + scale + "-cactus.png")
