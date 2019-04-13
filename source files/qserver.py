#!/usr/bin/env python
# Part of the socket program was adapted from https://www.geeksforgeeks.org/socket-programming-python/.
# I do not claim to own this code. The code was used as a template for creating the socket between server and client
import time              # Library used for delaying
import socket            # Library used for socket connection
import pip               # Library used to install the mysql package into the host machine
import sys               # Library used for error handling
import traceback
from threading import Thread
import mysql.connector   # Library used for mysql access
from mysql.connector import MySQLConnection, Error, errorcode

# The packet install code was based off user, Rikard Anglerud, on the following website
# https://stackoverflow.com/questions/12332975/installing-python-module-within-code
# The code allows for the mysql-connector-python package to be automatically installed in the users machine
# Code IS NOT MINE and I DO NOT CLAIM IT AS MY OWN. CODE is used to install a moddule needed for MYSQL connection
# Without the need for PIP
# Creates a connection to a mysql server (Free DB provided by UF)

# def install(package):
    # if hasattr(pip, 'main'):
    #     pip.main(['install', package])
    # else:
    #     pip._internal.main(['install', package])
    # # if __name__ == '__main__':
    #     install('mysql-connector-python')
# def client_thread(connection, ip, port, max_buffer_size = 5120):
#     is_active = True

#     while is_active:
#         client_input = receive_input(connection, max_buffer_size)

#         if "--QUIT--" in client_input:
#             print("Client is requesting to quit")
#             connection.close()
#             print("Connection " + ip + ":" + port + " closed")
#             is_active = False
#         else:
#             print("Processed result: {}".format(client_input))
#             connection.send("-".encode("utf8"))
# def receive_input(connection, max_buffer_size):
#     client_input = connection.recv(max_buffer_size)
#     client_input_size = sys.getsizeof(client_input)

#     if client_input_size > max_buffer_size:
#         print("The input size is greater than expected {}".format(client_input_size))

#     decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
#     return decoded_input
# def process_input(input_str):
#     print("Processing the input received from client")

#     return "Hello " + str(input_str).upper()
# def contestant_input(connection):
# connection.send("Hello World")

def create_socket():
    # Socket object with AF_INET = IPV4  & SOCK_STREAM = TCP connect
    socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketObj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Binds the address, blank for localhost, and port shared between client & server
    socketObj.bind(('',0))
    global port
    port = socketObj.getsockname()[1]
    print(port)
    print('Socket was successful')    # Success message prints if previous passed
    socketObj.listen(5)               # Maximum number of connections that can be queued
    return socketObj
def db_setup():    
    # install('mysql-connector-python')
    try:
        dbObj = mysql.connector.connect(user = 'paladine', password ='quizApp123', host ='mysql.cise.ufl.edu', database ='quizApp')
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
        sys.exit()
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
        sys.exit()
      else:
        print(err) 
    print('Database connection is successful!')
    return dbObj
def client_input(socketObj,dbObj):
    while True:
        conn,address = socketObj.accept()
        dbCursor =  dbObj.cursor()
        while True:
            userInput = conn.recv(1024).decode().strip()
            if len(userInput) > 0:
                if userInput == 'k':
                    print('Shuting Server', address)
                    conn.close()
                    dbObj.close()
                    socketObj.shutdown(socket.SHUT_RDWR)
                    socketObj.close()
                    sys.exit()
                elif userInput == 'q':
                    print('Client Closing')
                    conn.close()
                    break
                elif userInput == 'b':
                    contestantSocket = firstmakeConnection()
                    start_new_thread(testFunction,(contestantSocket,))
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
                            conn.send("%d" % (row[0]))
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
                            conn.send('Question not found')
                        else:
                            dbCursor.execute("DELETE FROM question where id = '%d' "  %(int(userQuestionNum)))
                            dbObj.commit()
                            conn.send('Row Deleted')
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
                        conn.send(result)
                    except Error as error:
                        conn.send('Question not found')
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
                        conn.send(result)
                    except Error as error:
                        conn.send('Empty Table')
                        continue
                    answer = conn.recv(1024)
                    print answer
                    if(row[4] == answer): conn.send('Correct Answer')
                    else: conn.send('Incorrect Answer')
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
                        if(len(set) < 1): conn.send('Invalid Arguments')
                    except Error as error:
                        conn.send('ERROR with arguements')
                        continue
                    for row in set:
                        if (row[4] == userAnswer): conn.send('Correct Answer')
                        else: conn.send('Incorrect Answer')
                elif userInput == 'h':
                    print('Helpful message already sent.........')
                else:
                    print('Sending data back to the client.......')
                    conn.send(userInput)

def main():
    socketObj = create_socket()     # Creates socke and returns obj
    dbObj =  db_setup()             # Create db connection and returns obj
    client_input(socketObj, dbObj)  # Passes objs to client input function (db and connection access)

main()