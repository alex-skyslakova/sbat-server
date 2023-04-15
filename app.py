import os
from threading import Thread

from bokeh.client import pull_session
from bokeh.embed import server_document, server_session
from bokeh.io.state import curstate
from flask import Flask, render_template
from tornado import process

from server import bk_worker

TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./static')
FIRST = True
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
port = os.environ.get('PORT', 8000)
import os
import signal
import subprocess



@app.route("/", methods=['GET', 'POST'])
def app_page():
    return  render_template("index.html", template="Flask", relative_urls=False)


@app.route("/analysis", methods=['GET'])
def analysis_page():
    global FIRST
    if FIRST == True:
        # command = "netstat -ano | findstr 8000"
        # c = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        # stdout, stderr = c.communicate()
        # pid = int(stdout.decode().strip().split(' ')[-1])
        # os.kill(pid, signal.SIGTERM)
        Thread(target=bk_worker).start()
    FIRST = False
    # session = pull_session(url="http://localhost:5006/bkapp")
    # session.close()
    #script = server_session(None, session.id, url='http://localhost:5006/bkapp')

    script = server_document('http://localhost:5006/bkapp')
    return render_template("Analysis.html",script=script, template="Flask", relative_urls=False)


@app.route("/datasets", methods=['GET', 'POST'])
def datasets_page():
    return render_template("Datasets.html", template="Flask", relative_urls=False)


@app.route("/contact", methods=['GET'])
def contact_page():
    return render_template("Contact.html", template="Flask", relative_urls=False)


@app.route("/about-project", methods=['GET'])
def project_page():
    return render_template("About-Project.html", template="Flask", relative_urls=False)


@app.route("/home", methods=['GET'])
def home_page():
    return render_template("index.html", template="Flask", relative_urls=False)


if __name__ == '__main__':
    #Thread(target=bk_worker).start()
    app.run(port=8000, host="0.0.0.0", debug=True)# in deployment
    from waitress import serve
    print("HEREEEE")
    #print(open("test.txt", "r").readlines())
    #serve(app)


