import flask
import tts
import pyttsx3

app = flask.Flask(__name__)
chime = "n/a"

def speak(text):
    print(text + " start")
    engine = pyttsx3.init()
    engine.say(text)
    #engine.setProperty("rate", 1)
    engine.runAndWait()
    print(text + " done")


@app.route('/', methods = ['POST', 'GET'])
def hello():
    global chime
    if flask.request.method == 'GET':
        return flask.render_template('index.html', chime=chime)
    elif flask.request.method == 'POST':
        data = dict(flask.request.form)
        
        if 'chime' in data.keys():
            chime = data['chime']
        if 'speech' in data.keys():
            speak(data['speech'])
        return flask.render_template('index.html', chime=chime)


if __name__ == '__main__':
    app.run(debug = True)