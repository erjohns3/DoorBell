import flask
import threading
import subprocess
import RPi.GPIO as GPIO
import pafy
import vlc
import time
import datetime
import host_ip
import os
import validators
import sys

app = flask.Flask(__name__)
host = host_ip.ip
url_file = "/home/pi/programming/python/doorbell_getter/url.txt"
time_file = "/home/pi/programming/python/doorbell_getter/time.txt"

#################################### logging

def write_to_log(msg):
    try:
        with open('/home/pi/programming/python/doorbell_getter/server_log.log', 'a') as f:
            nowstr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")                   
            strstr = 'date: {}, msg: {}'.format(nowstr, msg)
            f.write(strstr + '\n')
    except:
        pass

    print(msg)
    sys.stdout.flush()

#################################### audio

url = "null"
start_time = 0
Instance = vlc.Instance("prefer-insecure")
player = Instance.media_player_new()

def stop():
    global player
    player.stop()
    print("stop")
    print(player)
    sys.stdout.flush()

def play():
    global player
    global start_time
    global url
    player.stop()
    print("play")
    ret = player.play()
    print(ret)
    if ret != 0 :
        setURL(url)
    ret = player.play()
    player.set_time(start_time * 1000)
    print(ret)
    print(player)
    sys.stdout.flush()

def setURL(val):
    if not validators.url(val):
        return False

    global url
    global Instance
    global player

    if "youtu" in val:
        url = val
        video = pafy.new(url)
        best = video.getbestaudio()
        playurl = best.url
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        print("url set")
        print(player)
        sys.stdout.flush()

        f = open(url_file, "w")
        f.write(url)
        f.close()

def setTime(val):

    global start_time

    try:
        start_time = float(val)
    except ValueError:
        start_time = 0

    f = open(time_file, "w")
    f.write(start_time)
    f.close()


f = open(url_file, "r")
setURL(f.readline())
f.close()

f = open(time_file, "r")
setTime(f.readline())
f.close()

#################################### gpio signals

def onFall(channel):
    global chime_timer
    chime_timer = threading.Timer(8.0, stop)
    chime_timer.start()
    print("fall")
    sys.stdout.flush()

def onRise(channel):
    global chime_timer
    print("rise: ", time.time())
    sys.stdout.flush()
    chime_timer.cancel()
    chime_timer = threading.Timer(8.0, stop)
    chime_timer.start()
    play()

#button = gpiozero.Button(17)
chime_timer = threading.Timer(8.0, stop)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(11, GPIO.RISING, callback=onRise, bouncetime=200)
#GPIO.add_event_detect(11, GPIO.FALLING, callback=onFall, bouncetime=200)

#################################### text to speech

def speak(text):
    subprocess.Popen(['espeak', '-s', '80', text])

################################## http server

def monitor():
    while True:
        global player
        print("{}, {}, {}, {}".format(player, player.will_play(), player.get_state(), player.get_length()))
        time.sleep(600)

#monitor_thread = threading.Thread(target=monitor, args=())
#monitor_thread.start()

####################################

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods = ['POST', 'GET'])
def catch_all(path): 
    
    global url
    global host

    if flask.request.method == 'GET':
        return flask.render_template('index.html', url=url)
    elif flask.request.method == 'POST':
        
        if path == 'play':
            play()
        if path == 'stop':
            stop()
        if path == 'url' :
            setURL(flask.request.form['url'])
            setTime(flask.request.form['time'])
        if path == 'speech':
            speak(flask.request.form['speech'])
        
        return flask.render_template('index.html', url=url)


if __name__ == '__main__':
    app.run(host=host, debug=False)

