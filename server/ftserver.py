#!/usr/bin/env python

#   simple implementation of FTP server in python for CS372 online
#   USAGE:
#     1. In order to run the script w/o typing "python" give yourself
#        execute permissions. Run the following command in the shell:
#                 $ chmod +x ftserver.py
#
#     2. Then you have to run the script with the following command
#        (omit the square brackets)
#                 ./ftserver.py [port number]
#

import socket
import sys
import errno
import os

#functions
def getPort():
    """Get the port number
    to connect to from the command line arguments"""

    portNum = int(sys.argv[1])
    return portNum

def createControlSocket():
    """Creates a socket for the TCP control connection 
    and returns it, and handles appropriate exceptions"""
    
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    except socket.error:
        print "Error in socket creation"
        sys.exit()

def execCmd(connectionSocket, cmd):
    validCmd = False
    if 'list' in cmd or 'quit' in cmd:
        validCmd = True
        break
    elif 'get' in cmd and '.' in cmd:
        validCmd = True
         break


    if validCmd == False:
        connectionSocket.send('Invalid command entered; Valid commands are \'list\', \'get <filename>\', and \'quit\'')

def listenForCmd(controlSocket,portNum):
    """Waits for the command to be recieved from 
    the FTP client"""
    controlSocket.bind(('',portNum))
    controlSocket.listen(1)
    print 'Server is ready to recieve commands\n'
    while 1:
        connectionSocket, addr = controlSocket.accept()
        cmd = connectionSocket.recv(1024)
             
        execCmd(connectionSocket, cmd)  #Check if the command sent was valid and execute it if it is
        connectionSocket.close()

#main program
portNum = getPort() #get host and port numbers
controlSocket = createControlSocket() #create the socket for the TCP control connection

listenForCmd(controlSocket, portNum) # Await user commands from the server
