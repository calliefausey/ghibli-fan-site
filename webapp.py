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

app.secret_key = os.environ['SECRET_KEY']

url = 'mongodb://{}:{}@{}:{}/{}'.format(
	os.environ["MONGO_USERNAME"],
	os.environ["MONGO_PASSWORD"],
	os.environ["MONGO_HOST"],
	os.environ["MONGO_PORT"],
	os.environ["MONGO_DBNAME"])
    
client = pymongo.MongoClient(url)
db = client[os.environ["MONGO_DBNAME"]]
ghibli_forum = db['posts']

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
    return render_template('forum.html')

@app.route('/fan-quiz')
def fanQuiz():
    state = ""
    if "answer1" in request.form:
        state = "answer"
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
    else:
        state = "quiz"
    return render_template('fan-quiz.html', state = state)
	
@app.route('/answerPage',methods=['GET','POST'])
def renderAnswerPage():
    #Check answer here
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
    return render_template('answerPage.html', currentScore = score, highScore = session["highScore"])

@app.route('/posted', methods=['POST'])
def post():
	username = session['user_data']['login']
	message = request.form['message']
	try:
		post = {"username": username, "message": message}
		post_id = ghibli_forum.insert_one(post).inserted_id
		post_id
	except Exception as e:
		print("error")
		print(e)
        
	return render_template('home.html', past_posts = posts_to_db())
    
def posts_to_db():
	post_table = Markup("<table class='table table-bordered'> <tr> <th> User </th> <th> Ghibli </th> </tr>")
	try:
		for p in ghibli_forum.find():
			post_id= p["_id"]
			print("Username: " + p["username"] + " Message: " + p["message"])
			post_table += Markup("<tr> <td>" + p["username"] + "</td> <td>" + p["message"] + "</td> <td>" + "<form action = '/delete' method = 'post'> <button type='submit' name='delete' value='" + str(post_id) + "'>Delete</button></form>" + "</td>")
	except:
		print("Error")
	post_table += Markup("</table>")
	return post_table
    
@app.route('/delete', methods=['POST'])
def delete():
	id=request.form['delete']
	try:
		db.ghibli_forum.delete_one( { "_id" : ObjectId(id) } )	
	except Exception as e:
		print("error")
		print(e)
	return render_template('home.html', past_posts = posts_to_db())
	
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
    
if __name__ == '__main__':
    app.run()