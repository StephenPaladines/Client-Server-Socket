#!/usr/bin/env python

# Part of the socket program was adapted from https://www.geeksforgeeks.org/socket-programming-python/.
# I do not claim to own this code. The code was used as a template for creating the socket between server and client
import time              # Library used for delaying
import socket            # Library used for socket connection
import pip               # Library used to install the mysql package into the host machine
import sys               # Library used for error handling
import mysql.connector   # Library used for mysql access
from mysql.connector import MySQLConnection, Error

# The packet install code was based off user, Rikard Anglerud, on the following website
# https://stackoverflow.com/questions/12332975/installing-python-module-within-code
# The code allows for the mysql-connector-python package to be automatically installed in the users machine
# Code IS NOT MINE and I DO NOT CLAIM IT AS MY OWN. CODE is used to install a moddule needed for MYSQL connection
# Without the need for PIP

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])
        if __name__ == '__main__':
            install('mysql-connector-python')

# Catches an error with binding the socket to localhost and port #
try:
    # Socket object with AF_INET = IPV4  & SOCK_STREAM = TCP connect
    socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Binds the address, blank for localhost, and port shared between client & server
    socketObj.bind(('',4567))
except socket.error as error_message:
    print('Socket unsucessful\n' + 'Error Code:' + str(error_message[0]) + '\nError Message:' + str(error_message[1]))
    sys.exit();

print('Socket was successful')    # Success message prints if previous passed
socketObj.listen(1)               # Maximum number of connections that can be queued

# Creates a connection to a mysql server (Free DB provided by UF)
try:
    dbObj = mysql.connector.connect(user='paladine', password='quizApp123', host='mysql.cise.ufl.edu', database='quizApp')
    dbCursor =  dbObj.cursor()
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
print('Database connection is successful!')

while True:
    userInput = ""
    conn,address = socketObj.accept()
    conn.sendall('Connection established')
    conn.recv(1024)
    while True:
        userInput = conn.recv(1024).strip()
        print('received:' +  userInput)
        if userInput == 'k':
            # done
            print('Shuting Server', address)
            conn.close()
            dbObj.close()
            socketObj.shutdown(socket.SHUT_RDWR)
            socketObj.close()
            break
        elif userInput == 'q':
            # done
            print('Client Closing')
            conn.close()
            break
        elif userInput == 'p':
            # done
            print('Adding new question to db...')
            userTag = conn.recv(1024).strip()
            print(userTag + '\n')
            userName = conn.recv(1024).strip()
            print(userName + '\n')
            userQue = conn.recv(1024).strip()
            print(userQue + '\n')
            userAnswer = conn.recv(1024).strip()
            print(userAnswer + '\n')
            print(userTag + userName + userQue + userAnswer)
            try:
                dbCursor.execute("INSERT INTO question (tag,name,questions,answer) VALUES (%s,%s,%s,%s)",(userTag,userName,userQue,userAnswer))
                dbObj.commit()
                dbCursor.execute("SELECT id FROM question ORDER BY id DESC LIMIT 1")
                set = dbCursor.fetchall()
                for row in set:
                    conn.sendall("%d" % (row[0]))
            except Error as error:
                print(error)
            print(dbCursor.rowcount, "record inserted.")
        elif userInput == 'd':
            # done
            userQuestionNum = conn.recv(1024)
            print(userQuestionNum)
            if userQuestionNum == '-1':
                continue
            try:
                dbCursor.execute("SELECT * FROM question where id = '%d'" %(int(userQuestionNum)))
                set = dbCursor.fetchall()
                if(len(set) < 1):
                    conn.sendall('Question not found')
                else:
                    dbCursor.execute("DELETE FROM question where id = '%d' "  %(int(userQuestionNum)))
                    dbObj.commit()
                    conn.sendall('Row Deleted')
            except Error as error:
                print(error)
                continue
        elif userInput == 'g':
            # done
            userQuestion = conn.recv(1024)
            print(userQuestion)
            if(userQuestion == '-1'): continue
            try:
                dbCursor.execute("SELECT * FROM question where id = '%d'" %(int(userQuestion)))
                set = dbCursor.fetchall()
                if(len(set) < 1):
                    conn.send('No Question Found')
                    continue
                result = ''
                for row in set:
                    result = str(row[0]) + '\n'
                    result = result + row[2] + '\n'
                    result = result + row[3] + '\n'
                conn.sendall(result)
            except Error as error:
                conn.sendall('Question not found')
                continue
        elif userInput == 'r':
            # done
            answer = ''
            try:
                dbCursor.execute("SELECT * FROM question ORDER BY RAND() LIMIT 1")
                set = dbCursor.fetchall()
                result = ''
                for row in set:
                    result = str(row[0]) + '\n'
                    result = result + row[2] + '\n'
                    result = result + row[3] + '\n'
                conn.sendall(result)
            except Error as error:
                conn.sendall('Empty Table')
                continue
            answer = conn.recv(1024)
            print answer
            if(row[4] == answer): conn.sendall('Correct Answer')
            else: conn.sendall('Incorrect Answer')
        elif userInput == 'c':
            # done
            userInput = conn.recv(1024)
            userInput = userInput.split()
            userQuestion = userInput[0]
            userAnswer = userInput[1]
            print('Userquestion: ' + userQuestion + 'UserAnswer: ' + userAnswer)
            try:
                sql = "SELECT * FROM question WHERE id = %s"
                dbCursor.execute(sql,(userQuestion,))
                set = dbCursor.fetchall()
                if(len(set) < 1): conn.sendall('Invalid Arguments')
            except Error as error:
                conn.sendall('ERROR with arguements')
                continue
            for row in set:
                if (row[4] == userAnswer): conn.sendall('Correct Answer')
                else: conn.sendall('Incorrect Answer')
        elif userInput == 'h':
            print('Helpful message already sent')
            # done
        else:
            print('sending data back to the client')
            conn.sendall(userInput)
    if userInput == 'k':break