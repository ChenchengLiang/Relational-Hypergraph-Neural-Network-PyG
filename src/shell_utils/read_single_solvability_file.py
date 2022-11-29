import sys
sys.path.append("/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG")
from src.collect_results.utils import read_files,read_json_file

def main():
    file=sys.argv[1]
    print_filled_fields(file,"","")


def print_filled_fields(file,key_word_1="",key_word_2=""):
    file_list = [file]
    json_obj_list = read_files(file_list,file_type="solvability.JSON",read_function=read_json_file)
    collected_fields=[]
    for j in json_obj_list:
        for field in j:
            if field != "file_name" and field != "file_size" and j[field][0]!="10800000" and key_word_1 in field and key_word_2 in field:
                collected_fields.append([field,j[field]])
                #print(field,j[field])
    print("collected_fields",len(collected_fields))
    for f in sorted(collected_fields):
        print(f[0],f[1])


if __name__ == '__main__':
    main()