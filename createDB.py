import psycopg2
import boto3
import os

# D O   N O T   C O M M I T   T H E S E    V A R S ! ! !

ENDPOINT = os.getvar(endpoint)
PORT = os.getvar(port)
USER = os.getvar(user)
REGION = os.getvar(region)
DBNAME = "Quiz"


# AWS Variables
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'
session = boto3.Session(profile_name='RDSCreds')
client = boto3.client('rds')
token = client.generate_db_auth_token(DBHostname=ENDPOINT, port=PORT, DBUsername=USER, Region=REGION)

# Other Variables
questions = ["Question 1", "Question 2", "Question 3"]
correctAns = ["1", "2", "3"]
wrongAns = [["1a", "1b", "1c"],["2a", "2b", "2c"],["3a", "3b", "3c"]]

try:
    conn  = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=token)
    cur = conn.cursor
        
    createTables = ("CREATE TABLE HighScores (username VARCHAR(52), score INTEGER","CREATE TABLE Questions (question VARCHAR(255), right VARCHAR(255), wrong1 VARCHAR(255, wrong2 VARCHAR(255), wrong3 VARCHAR(255)")
    
    for command in createTables:
        cur.execute(command)

    for q in questions:
        cur.execute("INSERT INTO Questions (question) VALUES (%s)"(q))
    
    for a in correctAns:
        cur.execute("INSERT INTO Questions (right) VALUES (%s)"(a))
    
    for w1,w2,w3 in wrongAns:
        cur.execute("INSERT INTO  Questions (wrong1,wrong2,wrong3) VALUES (%s,%s,%s)"(w1,w2,w3))
    
    cur.close()
    conn.commit()

except Exception as e:
    print("Error:{}".format(e))

finally:
    if conn is not None:
        conn.close()