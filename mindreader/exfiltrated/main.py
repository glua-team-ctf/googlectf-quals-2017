from flask import Flask, request, abort
import re
import os
import logging

assert os.environ['FLAG']

app = Flask(__name__)

INDEX = open('index.html').read()

HALL_OF_SHAME = []

@app.route('/')
def index():
    for ip in request.headers.get('X-Forwarded-For', '').split(','):
        ip = ip.strip().lower()
        if ip in HALL_OF_SHAME:
            abort(403)

    if 'f' in request.args:
        try:
            f = request.args['f']
            if re.search(r'proc|random|zero|stdout|stderr', f):
                abort(403)
            elif '\x00' in f:
                abort(404)
            return open(f).read(4096)
        except IOError:
            abort(404)
    else:
        return INDEX
