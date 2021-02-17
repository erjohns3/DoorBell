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

app = flask.Flask(__name__)
host = host_ip.ip

#################################### audio

url = "null"
Instance = vlc.Instance("prefer-insecure")
player = Instance.media_player_new()

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


setURL("http://www.youtube.com/watch?v=TO7z2FYB_mo")

#################################### gpio signals

def stopChime():
    global player
    player.stop()
    print("stop chime: ", time.time())

def onFall(channel):
    global chime_timer
    chime_timer = threading.Timer(8.0, stopChime)
    chime_timer.start()
    print("fall")

def onRise(channel):
    global player
    global chime_timer
    print("rise: ", time.time())
    chime_timer.cancel()
    chime_timer = threading.Timer(8.0, stopChime)
    chime_timer.start()
    player.stop()
    player.play()

def write_to_log(msg):
    try:
        with open('/home/pi/programming/python/doorbell_getter/server_log.log', 'a') as f:
            nowstr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")                   
            strstr = 'date: {}, msg: {}'.format(nowstr, msg)
            f.write(strstr + '\n')
    except:
        pass

    print(msg)

#button = gpiozero.Button(17)
chime_timer = threading.Timer(8.0, stopChime)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(11, GPIO.RISING, callback=onRise, bouncetime=200)
#GPIO.add_event_detect(11, GPIO.FALLING, callback=onFall, bouncetime=200)

#################################### text to speech

# def thread_speaker(text):
    # write_to_log('starting text {}'.format(text))
    # os.system('espeak -s {} {}'.format(str(80), text))
    # write_to_log('finished text {}'.format(text))

def speak(text):
    #arr = ['espeak', '"{}"'.format(text)]
    #write_to_log('spawning process for text, with arguments: {}'.format(','.join(arr)))
    subprocess.Popen(['espeak', '-s', '80', text])
    #subprocess.Popen(arr)
    #write_to_log('finished spawning process for text: {}'.format(text))

################################## http server

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods = ['POST', 'GET'])
def catch_all(path): 
    
    global player
    global url
    global host

    if flask.request.method == 'GET':
        return flask.render_template('index.html', url=url)
    elif flask.request.method == 'POST':
        
        if path == 'play':
            player.play()
            print("playing")
        if path == 'stop':
            player.stop()
        if path == 'url' :
            setURL(flask.request.form['url'])
        if path == 'speech':
            speak(flask.request.form['speech'])
        
        return flask.render_template('index.html', url=url)


if __name__ == '__main__':
    write_to_log('starting server process')
    app.run(host=host, debug=False)

write_to_log('ending server process')
