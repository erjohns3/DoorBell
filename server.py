from flask import Flask, render_template, request
app = Flask(__name__)

chime = "n/a"

@app.route('/', methods = ['POST', 'GET'])
def hello():
    global chime
    if request.method == 'GET':
        return render_template('index.html', chime=chime)
    elif request.method == 'POST':
        data = dict(request.form)
        
        if 'chime' in data.keys():
            chime = data['chime']
            print (data['chime'])
        if 'speech' in data.keys():
            
            print (data['speech'])
        return render_template('index.html', chime=chime)


if __name__ == '__main__':
    app.run(debug = True)