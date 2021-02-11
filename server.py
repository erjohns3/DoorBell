import flask
import threading
import gpiozero
import pyttsx3
import pafy
import vlc


app = flask.Flask(__name__)
host = '192.168.86.43'

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

#button = gpiozero.Button(2)
#button.when_pressed = onPressed

#################################### text to speech

def thread_speaker(text):
    engine = pyttsx3.init()
    engine.say(text)
    #engine.setProperty("rate", 1)
    engine.runAndWait()

def speak(text):
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
        if path == 'stop':
            player.stop()
        if path == 'url' :
            setURL(flask.request.form['url'])
        if path == 'speech':
            speak(flask.request.form['speech'])
        
        return flask.render_template('index.html', url=url)


if __name__ == '__main__':
    app.run(host=host, debug = True, use_reloader=False)
