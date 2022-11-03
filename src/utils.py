import glob
import os
import json


def write_predicted_label_to_JSON_file(predicted_list,raw_predicted_list,file_name_list,task_type,root="../data/test_data"):
    predicted_dir=os.path.join(root,"predicted")
    make_dirct(predicted_dir)
    for f,p,rp in zip(file_name_list,predicted_list,raw_predicted_list):
        zip_name= f[0]
        file_name= zip_name[:-len(".zip")]
        if os.path.exists(zip_name):
            unzip_file(zip_name)

        new_field = ["predictedLabel", "predictedLabelLogit"]
        rp= [float(max(r)) for r in rp] if task_type == "multi_classification" else [float(r) for r in rp]
        p= [int(x) for x in p]
        new_filed_content = [p,rp]
        add_JSON_field(file_name, new_field, new_filed_content)

        base_name = os.path.basename(file_name)
        new_name=os.path.join(predicted_dir,base_name)
        os.rename(file_name,new_name)
        file_compress([new_name], os.path.join(new_name) + ".zip")
        if os.path.exists(new_name):
            os.remove(new_name)


def add_JSON_field(json_file="",new_field=[],new_field_content=[]):
    json_obj = {}
    with open(json_file) as f:
        json_obj = json.load(f)
    for field,content in zip(new_field,new_field_content):
        json_obj[field] = content
    if os.path.exists(json_file):
        os.remove(json_file)
    with open(json_file, 'w') as f:
        json.dump(json_obj, f, sort_keys=False,separators=(",",":"))

def get_file_list(folder,file_type,compress_type="zip"):
    file_list = []
    file_names = folder +"/" + "*"+file_type+compress_type if compress_type=="" else folder +"/" + "*"+file_type+"."+compress_type
    for f in glob.glob(file_names):
        base_name = os.path.basename(f)
        if "normalized" not in base_name and "simplified" not in base_name:
            file_list.append(f)
    return file_list


def remove_processed_file(root=""):
    for f in get_file_list(os.path.join(root,"processed"),file_type="pt",compress_type=""):
        os.remove(f)
    for f in get_file_list(os.path.join(root,"predicted"),file_type="JSON",compress_type="zip"):
        os.remove(f)

def file_compress(inp_file_names, out_zip_file):
    import zipfile
    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(out_zip_file, mode="w")
    try:
        for file_to_write in inp_file_names:
            zf.write(file_to_write, os.path.basename(out_zip_file)[:-len(".zip")], compress_type=compression)
    except FileNotFoundError as e:
        print(str(e))
    finally:
        zf.close()


def read_one_filed(file_name,field_name):
    with open(file_name) as f:
        loaded_graph = json.load(f)
    return loaded_graph[field_name]

def unzip_file(zip_file):
    if os.path.exists(zip_file):
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file))
    else:
        print("zip file "+zip_file+" not existed")



def manual_flatten(target_list):
    temp = []
    for x in target_list:
        for y in x:
            temp.append(y)
    return temp
def make_dirct(d):
    try:
        os.mkdir(d)
        return d
    except:
        print(str(d), "folder existed")
        return d