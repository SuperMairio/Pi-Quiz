from flask import Flask, render_template, request, redirect
import envs #envs.py just holds all my variables I dont want public
import random
import sys
import boto3
import psycopg2
import os
import make_response
from make_response.format import response_format
from subprocess import Popen, PIPE

FILEPATH = envs.filepath
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
rightPin = "14"
wrongPins = ["15", "23", "18"]
class QuizClass():
    answers = []
    quizDict ={ 
        "question": "",
        "correctAns":[],
        "allAns":[]
        }

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
        count = 3
        #n = random.randint(1,(count))

        while n in qsAsked:
            n = random.randint(1,(count))
        
        qsAsked.append(n)

        self.cur.execute("SELECT question, correct, wrong1, wrong2, wrong3 FROM Questions WHERE number = %i;" % (n))
        TUPLEanswers = self.cur.fetchone()
        self.quizDict["question"] = TUPLEanswers[0]
        self.quizDict["correctAns"].append(TUPLEanswers[1]) 
        self.quizDict["allAns"] = list(TUPLEanswers[1:4])
        
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
        command = FILEPATH + rightPin + "1 0 0" #flash green LED
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        for pin in wrongPins:
            command = FILEPATH + pin + "1 0 0" #flash blue LEDs
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

    except Exception as e:
        print("Error:{}".format(e))

    return redirect("/quiz", code=302)

@app.route('/quiz', methods= ['POST', 'GET'])
def quiz():
    try:
        prevCorrect = ans["correctAns"]
    except:
        pass

    quizObj.FetchAnswers()
    ans = quizObj.ShuffleAnswers()
    r = score["right"]
    w = score["wrong"]
    q = ans["question"]
    num = (len(qsAsked))
    answers = ans["allAns"]
    cLen = len(ans["correctAns"])
    correct = ans["correctAns"][(cLen - 2)]

    if num == 0:
        num = 1

    print("correct answer:", ans["correctAns"])
    
    if request.method == 'POST':
        print(request.form)
        print(correct)
        if request.form["answer"] == correct:
            print("right", score["right"])
            score["right"] += 1
            command = FILEPATH + rightPin + "1 0 0" #flash green LED
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        else:
            score["wrong"] += 1
            command = FILEPATH + wrongPins[score["wrong"] - 1] + "1 1 0" #turn next blue LED on
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

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