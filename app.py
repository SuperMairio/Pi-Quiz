from flask import Flask, render_template, request
import envs
import random
import sys
import boto3
import psycopg2
import os

ENDPOINT = envs.endpoint
PORT = envs.awsport
USER = envs.dbuser
REGION = envs.region
DBNAME = "Quiz"
PASSWORD = envs.password

# AWS Variables
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'
session = boto3.Session(profile_name='default')
client = boto3.client('rds')
token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

app = Flask(__name__)
def GetAnswers():
    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        answers = cur.execute("SELECT right, wrong1, wrong2, wrong3 FROM Questions;")
        cur.close()
        conn.commit()
        conn.close()
        return(answers)

    except Exception as e:
        print("Error:{}".format(e))
    
def ShuffleAnswers(question):
    answers = GetAnswers()
    shuffledAns = answers[question-1] # because the array is 0 indexed
    random.shuffle(shuffledAns)
    print(shuffledAns)
    return(shuffledAns)

def SetCookie():
    if request.method == "POST":
        questionNum +=1
        response = make_response(render_template("quiz.html"))
        response.set_cookie("QuestionNumber", questionNum)
        return(response)

# Web app functions
@app.route('/') #127.0.0.1:5000
def index(): #homepage
    ShuffleAnswers(0)
    return render_template("index.html")

@app.route('/', methods=['POST'])
def getUsername():
    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        username = request.form['username']
        cur.execute("INSERT INTO HighScores (username) VALUES ('%s');" % username)
        cur.close()
        conn.commit()
        conn.close()

    except Exception as e:
        print("Error:{}".format(e))

    return("")

@app.route('/quiz', methods= ['POST'])
def quiz():
    if not request.cookies.get("Number"):
        response = make_response("Creating Cookie")
        response.set_cookie("Question Number", num)

    return render_template("quiz.html")  

@app.route('/highScores')
def highScores():
    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        data = cur.execute("SELECT * FROM HighScores ORDER BY score DESC LIMIT 10;")
        cur.close()
        conn.commit()
        conn.close()
        return render_template('highscores.html', highscores = data)

    except Exception as e:
        print("Error:{}".format(e))
        return("Error:{}".format(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')