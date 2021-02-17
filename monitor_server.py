import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import subprocess
import datetime

the_path = "/home/pi/programming/python/doorbell_getter"
doorbell_git_path = os.path.join(the_path, "DoorBell")
os.chdir(doorbell_git_path)

server_file = os.path.join(doorbell_git_path, 'server.py')
server_call_out_file = os.path.join(the_path, 'server_process_output.txt')
hupper_out_file = os.path.join(the_path, 'monitor_server_logs.log')
python_to_run = '/usr/bin/python'

global proc; proc = None
global ourtime; ourtime = 0
global dont_reload_files_containing; dont_reload_files_containing = [
    '.git',
    '__pycache__'
]

def write_to_log(msg):
    with open(hupper_out_file, 'a') as f:
        nowstr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        strstr = 'date: {}, msg: {}'.format(nowstr, msg)
        f.write(strstr + '\n')
        print(strstr)

def restart_server():
    global ourtime;
    if time.time() < (ourtime + 1):
        return
    ourtime = time.time()
    write_to_log('server restart requested')
    global proc;
    if proc is not None:
        write_to_log('killing')
        try:
            proc.terminate()
        except:
            write_to_log('couldnt terminate process for some reason')
        write_to_log('killed')
        time.sleep(.5)

    while True:
        try:
            proc = subprocess.Popen(
                [python_to_run,  server_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            break
        except Exception as e:
            write_to_log('exception while running server.py, trying again in 5 seconds')
            write_to_log(e)
            time.sleep(5)

    write_to_log('ran subprocess')


class MyHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        global dont_reload_files_containing;
        if any(map(lambda x: x in event.src_path, dont_reload_files_containing)):
             return
        write_to_log(str(event))
        restart_server()

write_to_log('starting hupper process')
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, doorbell_git_path, recursive=True)
observer.start()
write_to_log('Observer started')
try:
    while True:
       time.sleep(1)
       if not proc or proc.poll() is not None:
            write_to_log('process is not running for some reason, restarting...')
            restart_server()
finally:
    write_to_log('Observer stopping for some reason...')
    observer.stop()
    observer.join()
