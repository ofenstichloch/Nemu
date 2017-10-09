import composer
from io import StringIO
from flask import Flask, request, render_template, redirect
from wtforms import Form, TextAreaField
from yaml import load
import threading
import console

app = Flask(__name__)
ioStatus = StringIO()
current_console = None
network = []

class ConfigInputForm(Form):
    graph = TextAreaField('Graph YAML')


@app.route('/', methods=['GET', 'POST'])
def front():
    form = ConfigInputForm(request.form)
    if request.method == 'POST':
        print("starting")
        t = threading.Thread(target=composer.create, args=[request.form['graph'], ioStatus, network])
        t.start()
        print("running")
    return render_template('front.html', form=form)


@app.route('/status')
def status():
    return ioStatus.getvalue()


@app.route('/main')
def main():
    global current_console
    global network
    if len(network) == 0:
        try:
            with open('/tmp/nemu.graph', 'r') as file:
                network = load(file)
        except:
            pass
    if current_console is not None:
        print("Stopping WS")
        current_console.stop()
        current_console = None
    current_console = console.console()
    current_console.start()
    nodes = network[0]
    edges = network[1]
    current_console.setNode("node1")

    return render_template('main.html', nodes=nodes, edges=edges)

@app.route('/close')
def close():
    global current_console
    current_console.stop()
    return "OK"

#def main():
#    composer.create()

