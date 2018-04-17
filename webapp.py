from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
import pymongo
import pprint
import os
import json
import sys

app = Flask(__name__)

app.debug = True

@app.route('/')
def home():
    return render_template('home.html', posts=posts_to_html())
    
if __name__ == '__main__':
    app.run()