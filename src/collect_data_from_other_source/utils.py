import time
import subprocess
import json
import os
def run_one_shell(shell_file_name, log_file):
    initiall_dict = {"solving_time": ["10800"], "satisfiability": ["-1"]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(initiall_dict, outfile,indent=4)

    run_shell_command = ["sh", shell_file_name]
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.PIPE, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    output = eld.stdout.read().decode('utf-8').strip()

    out_dict={"solving_time":[str(used_time)],"satisfiability":[output]}
    # Open a file for writing
    with open(log_file, "w") as outfile:
        # Write the dictionary to the file as JSON
        json.dump(out_dict, outfile,indent=4)


    return used_time
