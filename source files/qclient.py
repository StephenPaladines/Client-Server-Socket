#!/usr/bin/env python

# Part of the socket program was adapted from https://www.geeksforgeeks.org/socket-programming-python/.
# I do not claim to own this code. The code was used as a template for creating the socket between server and client

import socket # Library used for socket connection
import sys    # Library used for error handling

# Catches an error with binding the socket to localhost and port #

socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket object
try:
    host = sys.argv[1]
    port = sys.argv[2]
except:
    print("Missing arguments. Please try again.......")
    exit()

try:
    socketObj.connect((host,int(port)))        # Connection to server
except socket.error as error_message:
    print('Socket unsucessful\n' + 'Error Code:' + str(error_message[0]) + 'Error Message:' + str(error_message[1]))
    sys.exit();

print('Socket was successful')    # Success servInput prints if previous passed

while True:
    servInput = raw_input('> ')

    if(len(servInput) > 0):
        socketObj.send(servInput[0])       # Sends the first char in servInput
    else:
        continue

    if servInput == 'q':
        print('Closing client')
        socketObj.close()               #  Closes the socket from client-side
        break
    elif servInput == 'k':
        print('Closing server')
        socketObj.close()               #  Closes the server
        break
    elif servInput[0] == 'd':
        if len(servInput) < 2 and servInput != ' ':
            print('Missing question number') # Check if the argument is present
            socketObj.send('-1')
            continue
        else:
            servInput = servInput.split()
            j = 0
            while j < 700:
                j+=1
            socketObj.send(servInput[1])
            data = socketObj.recv(1024) # Receive response servInput
            print(data)
    elif servInput[0] == 'g':
        if len(servInput) < 2:            # Check if the argument is present
            print('Missing question number')
            socketObj.send('-1')
            continue
        else:
            servInput = servInput.split()
            j = 0
            while j < 500:
                j+=1
            socketObj.send(servInput[1])
            data = socketObj.recv(1024) # Receive response servInput
            print(data)
    elif servInput == 'r':
        data = socketObj.recv(1024) # Receive random question row
        print(data)
        userAnswer = raw_input()        # User answer to verify
        socketObj.send(userAnswer)
        data = socketObj.recv(1024) # Receive response servInput (fail or success)
        print(data)
    elif servInput[0] == 'c':
        if len(servInput) < 4:
            print('Missing all arguments') # Check if the argument is present
            continue
        else:
            servInput = servInput.split()
            j = 0
            while j < 500:
                j+=1
            socketObj.send(servInput[1] + ' ' + servInput[2])
            print(servInput[1] + ' ' + servInput[2])
            data = socketObj.recv(1024) # Receive response servInput
            print(data)
    elif servInput == 'h':
        print('If you need help, choose one of the following charater:\n k,q,h,c,r,k,d,g,p')
    elif servInput == 'p':
        userInput = raw_input()         # Enter question tag
        socketObj.send(userInput)
        userInput = raw_input()         # Enter question name
        socketObj.send(userInput)
        print('.')                      # Print first dot
        counter = 0
        question = ""
        while True:                     # Keep inserting answers (min 2)
            userAnswer = raw_input()    # Question answer
            if(userAnswer == '.' and counter > 1): break
            elif(len(userAnswer) < 1 or userAnswer == '.'): print('Enter more answers')
            else:
                print('.')
                question += (userAnswer + '\n.\n')
                counter += 1                # Verifies atleast two answers
        socketObj.send(question)     # Sends answers
        userCorrectAnswer = raw_input() # Enters valid answer
        socketObj.send(userCorrectAnswer)
        data = socketObj.recv(1024) # Receive response servInput
        print(data)
    else:
        print('Please enter a valid argument\n Enter ''h'' for help')