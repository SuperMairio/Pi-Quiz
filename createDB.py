import psycopg2
import boto3
import os
import envs

ENDPOINT = envs.endpoint
PORT = envs.awsport
USER = envs.dbuser
REGION = envs.region
DBNAME = "Quiz"
PASSWORD = envs.password


# AWS Variables
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'
session = boto3.Session(profile_name='root')
client = boto3.client('rds')
token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

# Other Variables
number = ["1","2","3"]
questions = ["Question 1", "Question 2", "Question 3"]
correctAns = ["1", "2", "3"]
wrongAns = [["1a", "1b", "1c"],["2a", "2b", "2c"],["3a", "3b", "3c"]]
usernames = ["mairi", "Cooler Mairi", "abc"]
scores = [2, 5, 1]
def ExampleData(cur): 
    for n, q, a, w in zip(number, questions, correctAns, wrongAns):
        cur.execute("INSERT INTO Questions (number, question,correct,wrong1,wrong2,wrong3) VALUES {'%s','%s','%s','%s','%s','%s'};" % (n,q,a,w[0],w[1],w[2]))

    for u, s in zip(usernames, scores):
        cur.execute("INSERT INTO HighScores (username, score) VALUES {'%s','%s'};" % (u,s))

def ClearTables(cur):
    clearTables = ("DELETE FROM Questions;", "DELETE FROM HighScores;")

    for c in clearTables:
        cur.execute(c)

    print("Tables cleared")

try:
    conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
    cur = conn.cursor()
        
    createTables = ("CREATE TABLE IF NOT EXISTS HighScores (username varchar(52) NOT NULL, score integer NOT NULL);","CREATE TABLE IF NOT EXISTS Questions (number integer NOT NULL, question varchar(255) NOT NULL, correct varchar(255) NOT NULL, wrong1 varchar(255) NOT NULL, wrong2 varchar(255) NOT NULL, wrong3 varchar(255) NOT NULL);")
    
    for command in createTables:
        cur.execute(command)

    #ClearTables(cur) #uncomment to clear all data from tables
    #ExampleData(cur) #uncomment to populate tables with random data
    
    cur.close()
    conn.commit()

except Exception as e:
    print("Error:{}".format(e))

finally:
    if conn is not None:
        conn.close()