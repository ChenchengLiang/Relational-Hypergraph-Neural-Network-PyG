
def get_task_by_folder_name(folder_name):
    if "template" in folder_name:
        return "template_binary_classification"
    elif "unsatcore" in folder_name:
        return "unsatcore_binary_classification"
    else:
        return "argument_binary_classification"

