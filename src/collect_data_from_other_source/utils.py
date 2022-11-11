import time
import subprocess
def run_one_shell(shell_file_name, log_file):
    run_shell_command = ["sh", shell_file_name]
    start = time.time()
    eld = subprocess.Popen(run_shell_command, stdout=subprocess.DEVNULL, shell=False)
    eld.wait()
    end = time.time()
    used_time = end - start
    with open(log_file, "w") as l:
        l.write("used_time:" + str(used_time))
    return used_time