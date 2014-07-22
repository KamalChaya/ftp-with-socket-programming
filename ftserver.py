#!/usr/bin/env/ python
#simple implementation of FTP server in python for CS372 online
#usage: ./ftserver.py [host name] [port number]

import socket

#functions
def getHostPort():
    """Get the hostName and port number
    to connect to from the command line arguments"""
    hostName = sys.argv[1]
    portNum = int(sys.argv[2])
    return hostName, portNum

def createControlSocket():
    """Creates a socket for the TCP control connection 
    and returns it, and handles appropriate exceptions"""
    
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    except socket.error:
        print "Error in socket creation"
        sys.exit()

def connectControlSocket(controlSocket, hostName, portNum):
    """Connects the socket to the host and port, and 
    handles any exceptions"""
    try:
        controlSocket.connect((hostName, portNum))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED: #Handling the exception of the socket connection being refused
            print "error: socket connection refused"
            sys.exit()
        else:
            print "Error: a socket exception occured"
            sys.exit(1)

    print 'Sucessfully established TCP control connection'

def listenForCmd(controlSocket,portNum):
    """Waits for the command to be recieved from 
    the FTP client"""
    controlSocket.bind('',portNum)
    controlSocket.listen(1)
    print 'Server is ready to recieve commands\n'
    while 1:
        connectionSocket, addr = controlSocket.accept()
        cmd = connectionSocket.recv(1024)
        print cmd
        connectionSocket.send("cmd recieved")
        connectionSocket.close()

#main program
hostName, portNum = getHostPort() #get host and port numbers
controlSocket = createControlSocket() #create the socket for the TCP control connection
connectControlSocket(controlSocket, hostName, portNum) # connect the control socket to the appropriate port/host
listenForCmd(controlSocket, portNum) # Await user commands from the server
