from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
#from bson.objectid import ObjectId

import pymongo
import pprint
import os
import json
import sys

app = Flask(__name__)

app.debug = True
"""app.secret_key = os.environ['SECRET_KEY']

url = 'mongodb://{}:{}@{}:{}/{}'.format(
	os.environ["MONGO_USERNAME"],
	os.environ["MONGO_PASSWORD"],
	os.environ["MONGO_HOST"],
	os.environ["MONGO_PORT"],
	os.environ["MONGO_DBNAME"])
    
client = pymongo.MongoClient(url)
db = client[os.environ["MONGO_DBNAME"]]
collection = db['posts']

oauth = OAuth(app)


#github = oauth.remote_app(
    #'github',
    #consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    #consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    #request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    #base_url='https://api.github.com/',
    #request_token_url=None,
    #access_token_method='POST',
    #access_token_url='https://github.com/login/oauth/access_token',  
    #authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
#)

@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}
    
@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/forum')
def forum():
    return render_template('forum.html', posts = posts_to_html())
    
@app.route('/mood-quiz', methods=['GET', 'POST'])
def moodQuiz():
    state = ""
    if "question1" in request.form:
        majority = ""
        A = 0
        B = 0
        C = 0
        for value in request.form:
            print(request.form[value])
            if request.form[value] == "A":
                A+=1
            if request.form[value] == "B":
                B+=1
            if request.form[value] == "C":
                C+=1
        if A >= B and A >= C:
            majority = "A"
            movieSuggestions = Markup("<p>Spirited Away, Howl's Moving Castle, or Kiki's Delivery Service</p>")
        elif B >= A and B >= C:
            majority = "B"
            movieSuggestions = Markup("<p>Ponyo or My Neighbor Totoro</p>")
        else:
            majority = "C"
            movieSuggestions = Markup("<p>Porco Rosso or Castle in the Sky</p>")
        return render_template('film-for-mood-quiz.html', suggestion = movieSuggestions, state = "answer")
    return render_template('film-for-mood-quiz.html', state = "quiz")
    
@app.route('/fan-quiz', methods=['GET', 'POST'])
def fanQuiz():
    state = ""
    if "answer1" in request.form:
        session["answer1"] = request.form["answer1"]
        session["answer2"] = request.form["answer2"]
        session["answer3"] = request.form["answer3"]
        session["answer4"] = request.form["answer4"]
        session["answer5"] = request.form["answer5"]
        score = 0
        if session["answer1"].lower() == "hayao miyazaki":
            score+=1
        if session["answer2"].lower() == "castle in the sky":
            score+=1
        if session["answer3"].lower() == "pig":
            score+=1
        if session["answer4"].lower() == "jiji":
            score+=1
        if session["answer5"].lower() == "forest":
            score+=1
        if "highScore" not in session:
            session["highScore"] = score
        elif score > session["highScore"]:
            session["highScore"] = score
        return render_template('fan-quiz.html', currentScore = score, highScore = session["highScore"], state = 'answer')
    else:
        return render_template('fan-quiz.html', state = 'quiz')

@app.route('/posted', methods=['POST'])
def post():
    username = session['user_data']['login']
    message = request.form['message']
    try:
        collection.insert(
            {"user": username, "post": message}
        )
    except Exception as e:
        print('Unable to load database')
        print(e)
    return render_template('forum.html', posts = posts_to_html())
    
def posts_to_html():
    try:
        table = Markup("<table class='table table-bordered'><tr><th>User</th><th>Post</th><th>Delete</th></tr>")
        for value in collection.find():
            table += Markup("<tr><td>" + value["user"] + "</td><td>" + value["post"] + "</td><td><form action='/delete' method='post'><button type='submit' name='delete' value='" + str(value["_id"]) + "'>Delete</button></form></td></tr>")
        table += Markup("</table>")
    except Exception as e:
        table = Markup('<p>There was an error loading the table data</p>')
        print(e)
    return table
    
@app.route('/delete', methods=['POST'])
def delete():
    #delete posts
    global collection
    collection.delete_one({"_id" : ObjectId(request.form['delete'])})
    return render_template('forum.html', posts=posts_to_html())
	
@app.route('/login')
def login():   
	return github.authorize(callback=url_for('authorized', _external=True, _scheme='httpS')) 

@app.route('/logout')
def logout():
	session.clear()
	return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
	resp = github.authorized_response()
	if resp is None:
		session.clear()
		message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
	else:
		try:
			session['github_token'] = (resp['access_token'], '') 
			session['user_data']=github.get('user').data
			message='You were successfully logged in as ' + session['user_data']['login']
		except Exception as inst:
			session.clear()
			print(inst)
			message='Unable to login, please try again.  '
	return render_template('message.html', message=message)
    
@app.route('/update-post')
def updatePost():
    return Markup("")

@app.route('/update-cancel')
def updateCancel():
    return Markup("<button id='toggle' value='post'>Post</button>")

if __name__ == '__main__':
    app.run()