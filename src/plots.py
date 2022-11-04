import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import mlflow
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix
import plotly.express as px
import numpy as np

plt.style.use("ggplot")


def loss_plot(train_loss_floats, valid_loss_floats):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(train_loss_floats))),
        y=train_loss_floats,
        name="train_loss"
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(valid_loss_floats))),
        y=valid_loss_floats,
        name="valid_loss"
    ))

    fig.update_layout(
        title='',
        xaxis_title='epocs',
        yaxis_title='loss')
    plot_name = "loss"
    save_file_name = "../figures/" + plot_name + ".html"
    # fig.update_yaxes(type="linear")
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)


def draw_label_pie_chart(num_label, learning_label, name=""):
    label_name_list = list(range(num_label))
    flat_list = [item for sublist in learning_label for item in sublist]
    values = [flat_list.count(i) for i in label_name_list]
    pull = [0.2 if v / sum(values) < 0.01 else 0 for v in values]  # if percentage < 0.01, pull it out from the pie
    fig = go.Figure(title=name+str(len(learning_label)),data=[go.Pie(labels=label_name_list, values=values, pull=pull)])

    save_file_name = "../figures/" + name + "-distribution.html"
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)
    return values


def draw_confusion_matrix(predicted_y, true_y, num_classes, name=""):
    label_list = list(range(num_classes))
    cm = confusion_matrix(true_y, predicted_y, labels=label_list)
    fig = px.imshow(cm, x=label_list, y=label_list, text_auto=True)
    fig.update_layout(
        title='confusion matrix',
        xaxis_title='predicted_y',
        yaxis_title='true_y')
    save_file_name = "../figures/" + name + "-confusion-matrix.html"
    fig.write_html(save_file_name)
    mlflow.log_artifact(save_file_name)


def plot_cactus(summary_folder, solvability_summary):
    max_time = np.max(np.max(np.array([item["solvingTime_list"] for item in solvability_summary.values()]))) / 1000
    # print("max_time s",max_time)
    cactus = {}
    time_limit = int(max_time) + 1
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
    #     draw_one_cactus(summary_folder,cactus,k)

    # draw_one_cactus(summary_folder, cactus, "")
    draw_one_cactus_plotly(summary_folder, cactus, key_word="", scale="linear")
    draw_one_cactus_plotly(summary_folder, cactus, key_word="", scale="log")


def draw_one_cactus_plotly(summary_folder, cactus, key_word, scale=""):
    # sort lines by solved problems for the highest time limit
    lines = []
    for k in cactus:
        if key_word in k:
            lines.append((len(cactus[k]), k, cactus[k]))
    lines.sort(reverse=True)

    fig = go.Figure()
    for line in lines:
        if key_word in line[1]:
            fig.add_trace(go.Scatter(
                x=list(range(len(line[2]))),
                y=line[2],
                name=line[1]
            ))

    fig.update_layout(  # legend_title_text='Trend',
        title='',
        xaxis_title='solved benchmarks',
        yaxis_title='time limit (s)')
    fig.update_yaxes(type=scale)
    fig.write_html(summary_folder + "/" + key_word + "-" + scale + "-cactus.html")
