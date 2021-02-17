import subprocess
import sys
import os
from datetime import datetime

URL = "https://github.com/erjohns3/DoorBell"
the_path = "/home/pi/programming/python/doorbell_getter"



doorbell_git_path = os.path.join(the_path, "DoorBell")
log_when_pull_path = os.path.join(the_path, "pull_git_periodically_logs.log")

os.chdir(doorbell_git_path)
res = subprocess.run([
    "git", "pull"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True)

with open(log_when_pull_path, "a") as f2:
    now = datetime.now()
    now_str = now.strftime("%m/%d/%Y, %H:%M:%S")
    txt = 'STDOUT: ' + res.stdout + ', STDERR: ' + res.stderr
    if "Already up to date." not in txt:
        f2.write("date: {}, txt: {}\n".format(now_str, txt))
