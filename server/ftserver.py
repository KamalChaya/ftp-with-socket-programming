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
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["controlport="])
    except getopt.GetoptError as err:
        print "USAGE: ./ftserver.py -c [controlport] \n OR : ./ftserver.py --controlport [controlport]\n"
               
    for o, a in opts:
        if o in "-c" or "--controlport":
            ctrlPort = a


    return ctrlPort        

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
        dataSocket.connect((hostName, dataPort))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED: #Handling the exception of the socket connection being refused
            print "error: socket connection refused"
            sys.exit(1)
        else:
            print "Error: a socket exception occured"
            sys.exit(1)


    print 'Sucessfully established TCP data connection\n'        

def execCmd(connectionSocket, cmd, dataPort, hostName):
    validCmd = False
    if '-l' or 'list' in cmd:
        validCmd = True
        
        #Initiate TCP data connection
        dataSocket = createSocket()
        connectDataSocket(dataSocket, hostName, dataPort)
        files = os.listdir(os.curdir)

        listStr = ''
        for i in files:
            listStr = listStr + i + '\n'

        dataSocket.send(listStr)    



    elif 'get' in cmd and '.' in cmd:
        validCmd = True
        dataSocket.send('get command received')



    if validCmd == False:
        connectionSocket.send('Invalid command entered; Valid commands are \'list\', and \'get <filename>\'')
    else:
        connectionSocket.send('valid command sent: ' + cmd)

def listenForCmd(controlSocket,portNum):
    """Waits for the command to be recieved from 
    the FTP client"""
    controlSocket.bind(('',int(portNum)))
    controlSocket.listen(1)
    print 'Server is ready to recieve commands\n'
    while 1:
        connectionSocket, addr = controlSocket.accept()
        received = connectionSocket.recv(1024)
        receivedArray = received.split(":")
        hostName = receivedArray[0]
        dataPort = int(receivedArray[1])
        cmd = receivedArray[2]


        execCmd(connectionSocket, cmd, dataPort, hostName)  #Check if the command sent was valid and execute it if it is
        connectionSocket.close()

#main program
ctrlPort = getPort() #get host and port numbers
controlSocket = createSocket() #create the socket for the TCP control connection

listenForCmd(controlSocket, ctrlPort) # Await user commands from the server
