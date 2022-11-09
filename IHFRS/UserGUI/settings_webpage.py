import os
import time
from flask import Flask, render_template, request, redirect
from multiprocessing import Event, Process, Queue
from configparser import ConfigParser

webServerProcess = None

app = Flask(__name__)


@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


@app.route('/video_stream/')
def video_stream():
    return "Hello World"


@app.route('/config/')
def config():
    return render_template('config.html')


@app.route('/wifi_set/')
def wifi_set():
    return render_template('wifi_set.html')


@app.route('/confirmation/')
def confirmation():
    return render_template('confirmation.html')


@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')


def main():
    app.debug = False
    app.run(host='0.0.0.0', port='4000')


if __name__ == '__main__':

    try:
        webServerProcess = Process(target=main)
        webServerProcess.start()
    except KeyboardInterrupt:
        webServerProcess.terminate()
        print("Terminated")
