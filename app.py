from flask import Flask, render_template
import random

app = Flask(__name__)

questions = ['a','a2','a3']
answers = [['1','2','3'],['a1','a2','a3'],['b1','b2','b3']]

def ShuffleAnswers(question):
    shuffledAns = answers[question]
    random.shuffle(shuffledAns)
    return(str(shuffledAns))

@app.route('/') #127.0.0.1:5000
def index(): #homepage
    return ShuffleAnswers(1)
    #return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')