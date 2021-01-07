from flask import Flask, render_template, request
import envs #envs.py just holds all my variables I dont want public
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
qsAsked = []
num = 0

def GetAnswers():
    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        count = cur.execute("SELECT COUNT number FROM Questions;")
        n = random.randint(0,(count-1))

        if n in qsAsked:
            n = random.randint(0,(count-1))
        
        qsAsked.append(n)

        cur.execute("SELECT question, correct, wrong1, wrong2, wrong3 FROM Questions WHERE number = %s;" % ('1'))
        answers = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
        return(answers) #a tuple NOT A LIST

    except Exception as e:
        print("Error:{}".format(e))
    
def ShuffleAnswers():
    answers = list(GetAnswers()) #must convert to list as tuples cannot be shuffled 
    del answers[0] # get rid of question and just have answers
    
    random.shuffle(answers)

    return(answers)

def SetCookie():
    num = len(qsAsked) +1
    if not request.cookies.get("Number"):
        response = make_response("Creating Cookie")
        response.set_cookie("Question Number", num)

# Web app functions
@app.route('/') #127.0.0.1:5000
def index(): #homepage
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
    answers = ShuffleAnswers()
    q = answers[0]
    ans1 = answers[1]
    ans2 = answers[2]
    ans3 = answers[3]
    ans4 = answers[4]
    num = request.cookies.get("Number")

    return render_template("quiz.html", questnum=num, question=q ,answer=ans1, answer2=ans2, answer3=ans3, answer4=ans4)  

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