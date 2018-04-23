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
    return render_template('home.html')

@app.route('/fan-quiz')
def fanQuiz():
    return render_template('fan-quiz.html')
	
@app.route('/answerPage',methods=['GET','POST'])
def renderAnswerPage():
    #Check answer here
    session["answer1"] = request.form["answer1"]
    session["answer2"] = request.form["answer2"]
    session["answer3"] = request.form["answer3"]
    session["answer4"] = request.form["answer4"]
    session["answer5"] = request.form["answer5"]
    score = 0
    if session["answer1"].lower() == "Hayao Miyazaki":
        score+=1
    if session["answer2"].lower() == "Castle in the Sky":
        score+=1
    if session["answer3"].lower() == "pig":
        score+=1
    if session["answer4"].lower() == "Jiji":
        score+=1
    if session["answer5"].lower() == "forest":
        score+=1
    if "highScore" not in session:
        session["highScore"] = score
    elif score > session["highScore"]:
        session["highScore"] = score
    return render_template('answerPage.html', currentScore = score, highScore = session["highScore"])
    
if __name__ == '__main__':
    app.run()