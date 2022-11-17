import asyncio
import os
import time
from threading import Thread

import requests
from bokeh.embed import server_document, components
from bokeh.io import curdoc
from flask import Flask, render_template, Response, request
from flask_cors import CORS, cross_origin
from tornado import process
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, Application
from tornado.wsgi import WSGIContainer
from werkzeug import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from config import FLASK_PORT, FLASK_URL, FLASK_PATH, get_bokeh_port, BOKEH_URL
from server import modify_doc, bk_worker, LOG
from wsproxy import WebSocketProxy

TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
port = os.environ.get('PORT', 8000)


@app.route("/", methods=['GET', 'POST'])
def app_page():
    return render_template("index.html", template="Flask", relative_urls=False)


@app.route("/analysis", methods=['GET'])
def analysis_page():
    #Thread(target=bk_worker).start()
    doc = modify_doc(curdoc())
    script, div = components(doc.roots[0], doc.roots[1])

    #script = server_document('https://localhost:5006/bkapp')
    return render_template("Analysis.html",script=script,div=div, template="Flask", relative_urls=False)


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

#
# app1 = DispatcherMiddleware(app, {
#     '/api': bk_worker,
# })
# # if __name__ == '__main__':
# #     app1.run(port=8000)  # host="0.0.0.0" in deployment
# from waitress import serve
# run_simple("localhost", port, app1)


@app.route('/<path:path>', methods=['GET'])
@cross_origin(origins='*')
def proxy(path):
    """ HTTP Proxy """
    query = ''
    if request.query_string is not None:
        query = '?' + request.query_string.decode("utf-8")

    bokeh_url = BOKEH_URL.replace('$PORT', get_bokeh_port())
    request_url = f"{bokeh_url}/{path}{query}"
    resp = requests.get(request_url)
    excluded_headers = ['content-length', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response


def start_tornado():
    """Start Tornado server to run a flask app in a Tornado
       WSGI container.

    """
    asyncio.set_event_loop(asyncio.new_event_loop())
    container = WSGIContainer(app)
    serverr = Application([
        (r'/bkapp/ws', WebSocketProxy, dict(path='/bkapp')),
        (r'.*', FallbackHandler, dict(fallback=container))
    ])
    serverr.listen(port=FLASK_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    THREAD = Thread(target=start_tornado, daemon=True)
    THREAD.start()
    LOG.info("Flask + Bokeh Server App Running at %s", FLASK_URL + FLASK_PATH)
    while True:
        time.sleep(0.01)

