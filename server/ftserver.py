#!/usr/bin/env python
#
#   Programming assignment 1 for cs372 online by Kamal Chaya
#   
#   simple implementation of FTP server in python 
#   USAGE:
#     1. In order to run the script w/o typing "python" give yourself
#        execute permissions. Run the following command in the shell:
#                 chmod +x ftserver.py
#
#     2. Then you have to run the script with the following command
#        (omit the square brackets)
#                 ./ftserver.py [port number]
#

import socket
import sys
import errno
import os
import getopt

#functions
def getPort():
    """Get the port number
    to connect to from the command line arguments"""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:h:")
    except getopt.GetoptError as err:
        print "USAGE: ./ftserver.py -c [controlport] -h [hostname] \n"
               
    ctrlPort = None
    clientHostName = None

    for o, a in opts:
        if o == "-c":
            ctrlPort = a
        elif o == "-h":
            clientHostName = a

    if '.engr.oregonstate.edu' not in clientHostName:
        clientHostName = clientHostName + '.engr.oregonstate.edu'


    return ctrlPort, clientHostName        

def createSocket():
    """Creates a socket for the TCP control connection 
    and returns it, and handles appropriate exceptions"""
    
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    except socket.error:
        print "Error in socket creation"
        sys.exit()

def connectDataSocket(dataSocket, hostName, dataPort):
    """Connects the socket to the host and port, and handles
    any exceptions"""

    try:
        dataSocket.connect((hostName, int(dataPort)))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED: #Handling the exception of the socket connection being refused
            print "error: socket connection refused"
            sys.exit(1)
        else:
            print "Error: a socket exception occured"
            sys.exit(1)


    print 'Sucessfully established TCP data connection\n'        

def checkCmd(connectionSocket, cmd):
    validCmd = False
    if 'list' == cmd:
        validCmd = True
 
    elif 'get' in cmd and '.' in cmd:
        validCmd = True

    if validCmd == False:
        connectionSocket.send('Invalid command entered; Valid commands are \'list\', and \'get <filename>\'')
    else:
        connectionSocket.send('valid command sent: ' + cmd)

    return validCmd    



def listenForCmd(controlSocket,portNum,clientHostName):
    """Waits for the command to be recieved from 
    the FTP client"""
    controlSocket.bind(('',int(portNum)))
    controlSocket.listen(1)
    print 'Server is ready to recieve commands\n'
    while 1:
        connectionSocket, addr = controlSocket.accept()
        received = connectionSocket.recv(1024)
        receivedArray = received.split(":")

        dataPort = receivedArray[0]
        cmd = receivedArray[1]

        print clientHostName + " " + dataPort + " " + cmd + "\n"

        validCmd = checkCmd(connectionSocket, cmd)  #Check if the command sent was valid and execute it if it is
        
        if validCmd == False:
           print 'Invalid command\n' 
           connectionSocket.close()
           sys.exit(1)

        else:
           dataSocket = createSocket()
           received = connectionSocket.recv(1024)
           if received == 'valid cmd received':
               connectDataSocket(dataSocket, clientHostName, dataPort)
               if cmd == 'list':
                   files = os.listdir(os.curdir)
                   fileStr = ''
                   for i in files:
                       fileStr = fileStr + i + '\n'
                   dataSocket.send(fileStr+"end")    


           dataSocket.close()        

        connectionSocket.close()

#main program
ctrlPort, clientHostName = getPort() #get host and port numbers
controlSocket = createSocket() #create the socket for the TCP control connection
listenForCmd(controlSocket, ctrlPort, clientHostName) # Await user commands from the server
