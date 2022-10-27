from utils import read_solvability_JSON

def main():
    print_filled_fields("predicateGeneratorTime","")


def print_filled_fields(key_word_1="",key_word_2=""):
    file_list = ["/home/cheli243/PycharmProjects/Relational-Hypergraph-Neural-Network-PyG/benchmarks/test/train_data/chc-LIA-non-lin_005.smt2.zip"]
    json_obj_list = read_solvability_JSON(file_list)
    collected_fields=[]
    for j in json_obj_list:
        for field in j:
            if j[field][0]!="10800000" and key_word_1 in field and key_word_2 in field:
                collected_fields.append([field,j[field]])
                #print(field,j[field])
    print("collected_fields",len(collected_fields))
    for f in sorted(collected_fields):
        print(f[0],f[1])


if __name__ == '__main__':
    main()