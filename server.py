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
import alsaaudio

app = flask.Flask(__name__)
host = host_ip.ip
url_file = "/home/pi/programming/python/doorbell_getter/url.txt"
skip_file = "/home/pi/programming/python/doorbell_getter/skip.txt"
duration_file = "/home/pi/programming/python/doorbell_getter/duration.txt"

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

def stop():
    global player
    player.stop()
    print("stop")
    print(player)
    sys.stdout.flush()

def play():
    global player
    global skip
    global duration
    global duration_timer
    global url
    player.stop()
    if time.time() - last_reset > 600:
       resetPlayer() 
       print("reset player")        
    player.play()
    print("play")
    player.set_time(int(skip*1000))
    duration_timer.cancel()
    if duration > 0:
        duration_timer = threading.Timer(duration, stop)
        duration_timer.start()
    print(player.get_time())
    sys.stdout.flush()

def resetPlayer():
    global url
    global Instance
    global player
    video = pafy.new(url)
    best = video.getbestaudio()
    playurl = best.url
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    last_reset = time.time()

def setURL(val):
    global url
    global url_file
    global Instance
    global player
    if not validators.url(val):
        return False
    if "youtu" in val:
        url = val
        resetPlayer()
        print("url set")
        print(player)
        sys.stdout.flush()

        f = open(url_file, "w")
        f.write(url)
        f.close()

def setSkip(val):
    global skip
    global skip_file
    try:
        skip = float(val)
    except ValueError:
        return
    skip = max(0, skip)
    print("skip valid: " + val)
    sys.stdout.flush()
    f = open(skip_file, "w")
    f.write(str(skip))
    f.close()

def setDuration(val):
    global duration
    global duration_file
    try:
        duration = float(val)
    except ValueError:
        return
    if duration <= 0:
        duration_file = -1
    print("duration valid: " + val)
    sys.stdout.flush()
    f = open(duration_file, "w")
    f.write(str(duration))
    f.close()


url = "null"
skip = 0.0
last_reset = 0
duration = -1
duration_timer = threading.Timer(duration, stop)
Instance = vlc.Instance("prefer-insecure")
player = Instance.media_player_new()

f = open(url_file, "r")
setURL(f.readline())
f.close()

f = open(skip_file, "r")
setSkip(f.readline())
f.close()

f = open(duration_file, "r")
setDuration(f.readline())
f.close()

#################################### volume

mixer = alsaaudio.Mixer()
volume = mixer.getvolume()[0]

def setVolume(val):
    global volume
    try:
        volume = int(val)
        print("volume valid: " + val)
    except:
        print("volume invalid: " + val)
    volume = min(100, max(0, volume))
    mixer.setvolume(volume)
    volume = mixer.getvolume()[0]

#################################### gpio signals

def onRise(channel):
    print("rise: ", time.time())
    sys.stdout.flush()
    play()

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

    if flask.request.method == 'POST':
        
        if path == 'play':
            play()
        elif path == 'stop':
            stop()
        elif path == 'url' :
            setURL(flask.request.form['url'])
            setSkip(flask.request.form['skip'])
            setDuration(flask.request.form['duration'])
        elif path == 'speech':
            speak(flask.request.form['speech'])
        elif path == 'volume':
            setVolume(flask.request.form['volume'])
        
    return flask.render_template('index.html', url=url, skip=skip, duration=duration, volume=volume)


if __name__ == '__main__':
    app.run(host=host, debug=False)

