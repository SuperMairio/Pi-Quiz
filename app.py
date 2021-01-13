from flask import Flask, render_template, request, redirect
import envs #envs.py just holds all my variables I dont want public
import random
import sys
import boto3
import psycopg2 # for postgresql
import os
import make_response
from make_response.format import response_format 
from subprocess import Popen, PIPE # for connecting to Pi 

FILEPATH = envs.filepath
ENDPOINT = envs.endpoint
PORT = envs.awsport
USER = envs.dbuser
REGION = envs.region
DBNAME = "Quiz"
PASSWORD = envs.password

app = Flask(__name__)
qsAsked = []
score = {"right":0, "wrong":0}
username = ""
rightPin = "14"
wrongPins = ["15", "23", "18"]
class QuizClass(): # Gets questions and shuffles answers
    answers = []
    quizDict ={ 
        "question": "",
        "correctAns":[],
        "allAns":[]
        }

    def __init__(self):
        self.conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        self.cur = self.conn.cursor()

    def __del__(self): # Cleans up 
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def FetchAnswers(self): # Gets question and answers
        self.cur.execute("SELECT number FROM Questions;")
        qNumber = self.cur.fetchall()
        count = 3
        n = random.randint(1,(count))

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

    def ShuffleAnswers(self): # shuffles answer order 
        random.shuffle(self.quizDict["allAns"])
        return(self.quizDict)
        
quizObj = QuizClass()

# Web app functions
@app.route('/', methods=['GET']) # 0.0.0.0:5000
def index(): #homepage
    return render_template("index.html")

@app.route('/', methods=['POST'])
def getUsername(): # takes username from POST and puts it in the database, as well as making all LEDs flash to show they are working
    allPins = wrongPins
    allPins.append(rightPin)

    try:
        conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
        cur = conn.cursor()
        username = request.form['username']
        cur.execute("INSERT INTO HighScores (username) VALUES ('%s');" % username)
        cur.close()
        conn.commit()

        for pin in allPins:
            command = FILEPATH + pin + "1 0 0" #flash all LEDs
            os.system(command.split())
            #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            #output, error = process.communicate()

    except Exception as e:
        print("Error:{}".format(e))

    return redirect("/quiz", code=302)

@app.route('/quiz', methods= ['POST', 'GET'])
def quiz(): # displays question and answers 
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
    elif num == 3:
        score["wrong"] = 3 #For example purposes end the quiz after three questions

    print("correct answer:", ans["correctAns"])
    
    if request.method == 'POST': # checks answer against the correct one
        print(request.form)
        print(correct)
        if request.form["answer"] == correct:
            print("right", score["right"])
            score["right"] += 1
            command = FILEPATH + rightPin + "1 0 0" #flash green LED
            os.system(command.split())
            #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            #output, error = process.communicate()
        else:
            score["wrong"] += 1
            wrongPin = wrongPins[score["wrong"] - 1]
            command = FILEPATH + wrongPin + "1 1 0" #turn next blue LED on
            os.system(command.split())
            #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            #output, error = process.communicate()

    return (render_template("quiz.html", questnum=num, question=q ,answers=answers, wrong=w, right=r))

@app.route('/highScores', methods = ['POST'])
def highScores(): # displays top ten scores
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
    app.run(debug=True, host='0.0.0.0') # gives me verbose error messages when something breaks
