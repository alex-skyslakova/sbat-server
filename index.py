import os
from threading import Thread

from bokeh.embed import server_document
from flask import Flask, render_template
from tornado import process

from server import bk_worker

TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
port = os.environ.get('PORT', 8000)


@app.route("/", methods=['GET', 'POST'])
def app_page():
    return render_template("index.html", template="Flask", relative_urls=False)


@app.route("/analysis", methods=['GET'])
def analysis_page():
    Thread(target=bk_worker).start()
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
    app.run(port=8000)  # host="0.0.0.0" in deployment

