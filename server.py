import flask
import threading
import subprocess
import gpiozero
import pafy
import vlc
import datetime
import host_ip
import os

app = flask.Flask(__name__)
host = host_ip.ip

#################################### audio

url = "null"
Instance = vlc.Instance()
player = Instance.media_player_new()

def setURL(val):
    global url
    global Instance
    global player

    if val[0:30] == "https://www.youtube.com/watch?" :
        url = val
        video = pafy.new(url)
        best = video.getbestaudio()
        playurl = best.url
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)


setURL("https://www.youtube.com/watch?v=TO7z2FYB_mo")

#################################### gpio signals

def onPressed():
    print("play")

def write_to_log(msg):
    with open('/home/pi/programming/python/doorbell_getter/server_log.log', 'a') as f:
        nowstr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")                   
        strstr = 'date: {}, msg: {}'.format(nowstr, msg)
        f.write(strstr + '\n')
        print(msg)

button = gpiozero.Button(2)
button.when_pressed = onPressed

#################################### text to speech

def thread_speaker(text):
    write_to_log('starting text {}'.format(text))
    # subprocess.run(['espeak', '-s', '80', text])
    os.system('espeak -s {} {}'.format(str(80), text))
    write_to_log('finished text {}'.format(text))

def speak(text):
    write_to_log('spawning thread for text')
    x = threading.Thread(target=thread_speaker, args=(text,))
    x.start()

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
    app.run(host=host)

write_to_log('ending server process')
