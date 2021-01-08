from flask import Flask, render_template, request
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
num = 0
#answers = []
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
        print("SELECT question, correct, wrong1, wrong2, wrong3 FROM Questions WHERE number = %i;" % (n))
        TUPLEanswers = self.cur.fetchone()
        print("TUPLEaNS:" , TUPLEanswers[4])
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

    return("")

@app.route('/quiz', methods= ['POST'])
def quiz():
    #quizObj = QuizClass()
    quizObj.FetchAnswers()
    ans = quizObj.ShuffleAnswers()
    print(quizObj.quizDict)
    num = len(qsAsked) +1
    
    q = ans["question"]
    ans1 = ans["allAns"][0]
    ans2 = ans["allAns"][1]
    ans3 = ans["allAns"][2]
    ans4 = ans["allAns"][3]
    
    if len(qsAsked) == 0:
        resp = make_response(render_template("quiz.html", questnum=num, question=q ,answer=ans1, answer2=ans2, answer3=ans3))
        resp.set_cookie("Number", num)
        print("cookie", request.cookies.get("Number"))
        num = request.cookies.get("Number")

        return resp
    return render_template("quiz.html", questnum=num, question=q ,answer=ans1, answer2=ans2, answer3=ans3, answer4=ans4)

@app.route('/highScores')
def highScores():
    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        cur.execute("SELECT * FROM HighScores ORDER BY score DESC LIMIT 10;")
        data = list(cur.fetchall())
        print(data)
        cur.close()
        conn.commit()
        return render_template('highscores.html', highscores = data)

    except Exception as e:
        print("Error:{}".format(e))
        return("Error:{}".format(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')