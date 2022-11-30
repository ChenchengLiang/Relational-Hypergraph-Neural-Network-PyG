
from utils import read_files,read_json_file
from src.utils import get_file_list, make_dirct







def main():
    folder=""
    for file in get_file_list(folder,"smt2"):
        print(file)
        file_name=file[:-len(".zip")]



if __name__ == '__main__':
    main()