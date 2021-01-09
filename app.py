from flask import Flask, render_template, request, redirect
import envs #envs.py just holds all my variables I dont want public
import random
import sys
import boto3
import psycopg2
import os
import make_response
from make_response.format import response_format

ENDPOINT = envs.endpoint
PORT = envs.awsport
USER = envs.dbuser
REGION = envs.region
DBNAME = "Quiz"
PASSWORD = envs.password

# AWS Variables
# os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'
# session = boto3.Session(profile_name='default')
# client = boto3.client('rds')
# token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

app = Flask(__name__)
qsAsked = []
score = {"right":0, "wrong":0}
username = ""
class QuizClass():
    answers = []
    quizDict = {}

    def __init__(self):
        self.conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def FetchAnswers(self):
        self.cur.execute("SELECT number FROM Questions;")
        qNumber = self.cur.fetchall()
        count = 3 #len(list(qNumber))
        n = random.randint(1,(count))

        while n in qsAsked:
            n = random.randint(1,(count))
        
        qsAsked.append(n)

        self.cur.execute("SELECT question, correct, wrong1, wrong2, wrong3 FROM Questions WHERE number = %i;" % (n))
        TUPLEanswers = self.cur.fetchone()
        self.quizDict = {
            "question": TUPLEanswers[0],
            "correctAns": TUPLEanswers[1],
            "allAns":list(TUPLEanswers[1:5])
        }
        
    def GetAnswers(self):
        return(self.quizDict)

    def ShuffleAnswers(self):
        random.shuffle(self.quizDict["allAns"])
        return(self.quizDict)
        
quizObj = QuizClass()

# Web app functions
@app.route('/', methods=['GET']) # 0.0.0.0:5000
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

    except Exception as e:
        print("Error:{}".format(e))

    return redirect("/quiz", code=302)

@app.route('/quiz', methods= ['POST', 'GET'])
def quiz():
    #quizObj = QuizClass()
    quizObj.FetchAnswers()
    ans = quizObj.ShuffleAnswers()
    r = score["right"]
    w = score["wrong"]
    q = ans["question"]
    num = (len(qsAsked))
    print("num", num)
    answers = ans["allAns"]
    correct = ans["correctAns"]

    if num == 0:
        num = 1

    print("correct answer:", ans["correctAns"])
    
    if request.method == 'POST':
        if correct in request.form['answer']:
            print("right", score["right"])
            score["right"] += 1
        else:
            score["wrong"] += 1
            print("wrong", score["wrong"])
    #if request.form.validate_on_submit():
    #   if correct in request.form():
    #     print("right", score["right"])
    # else:
        #    score["wrong"] += 1
        #   print("wrong", score["wrong"])

    return (render_template("quiz.html", questnum=num, question=q ,answers=answers, wrong=w, right=r))

@app.route('/highScores', methods = ['POST'])
def highScores():
    try:
        scores = score["right"]
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        cur.execute("INSERT INTO HighScores (score) VALUES (%i) WHERE username = ('%s')" % (scores, username))
        cur.execute("SELECT * FROM HighScores ORDER BY score DESC LIMIT 10;")
        data = list(cur.fetchall())
        cur.close()
        conn.commit()
        return render_template('highscores.html', highscores = data)

    except Exception as e:
        print("Error:{}".format(e))
        return("Error:{}".format(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')