from flask import Flask, render_template, request
import random
import sys
import boto3
import psycopg2
import os

ENDPOINT = os.getenv(endpoint)
PORT = os.getenv(port)
USER = os.getenv(user)
REGION = os.getenv(region)
DBNAME = "Quiz"

# AWS Variables
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'
session = boto3.Session(profile_name='dbmaster')
client = boto3.client('rds')
token = client.generate_db_auth_token(DBHostname=ENDPOINT, port=PORT, DBUsername=USER, Region=REGION)

app = Flask(__name__)

try:
    conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=token)
    cur = conn.cursor

except Exception as e:
    print("Error:{}".format(e))

# Database functions
def GetAnswers():
    answers = cur.execute("SELECT right, wrong1, wrong2, wrong3 FROM Questions;")
    return(answers)
def ShuffleAnswers(question):
    answers = GetQuestions()
    shuffledAns = answers[question-1] # because the array is 0 indexed
    random.shuffle(shuffledAns)
    return(shuffledAns)

# Web app functions
@app.route('/') #127.0.0.1:5000
def index(): #homepage
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getUsername():
    username = request.form['username']

    cur.execute("INSERT INTO HighScores (username) VALUES (%s);"(username))

    cur.close()
    conn.commit()

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')  

@app.route('/highScores')
def highScores():
    data = cur.execute("SELECT * FROM HighScores order by DESC LIMIT 10;")
    return render_template('highscores.html', highscores = data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

conn.close()