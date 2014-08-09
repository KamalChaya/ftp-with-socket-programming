#!/usr/bin/env python
#
#   Programming assignment 1 for cs372 online by Kamal Chaya
#
#   Simple implementation of FTP client in python
#   USAGE:
#     1. In order to run the script w/o typing "python" give yourself
#        execute permissions. Run the following command in the shell:
#                 chmod +x ftclient.py
#
#     2. Then you have to run the script with the following command 
#        (without the square brackets):
#                 ./ftclient.py -h [hostname] -d [dataport] -c [controlport] [-l or -g <filename> for list or get]
#                 ./ftclient.py --host [hostname] --dataport [dataport] --controlport [controlport] [--list or --get <filename>]
#        
#

import socket
import sys
import errno
import os
import getopt

#functions
def getHostPortCmd():
    """Get the hostName, command, and port number
    to connect to from the command line arguments"""
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:c:d:", ["cmd="])
    except getopt.GetoptError as err:
        print "USAGE:  ./ftclient.py -h [hostname] -d [dataport] -c [controlport] [-l or -g <filename> for list or get] \n"
        print "OR: ./ftclient.py --host [hostname] --dataport [dataport] --controlport [controlport] [--list or --get <filename>]\n"
        sys.exit(1)

    hostName = None
    ctrlPort = None
    dataPort = None
    cmd = None   

    
    for o, a in opts:
        if o in ("-h"):
            hostName = a
        elif o in ("-c"):
            ctrlPort = a
        elif o in ("-d"):
            dataPort = a
        elif o in ("--cmd"):
            cmd = a

    if '.engr.oregonstate.edu' not in hostName:
        hostName = hostName + '.engr.oregonstate.edu'


        
    return hostName, ctrlPort, dataPort, cmd

def createSocket():
    """Creates a TCP socket
    and returns it, and handles the appropriate exceptions"""

    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    except socket.error:
        print "Error in socket creation"
        sys.exit(1)

def connectControlSocket(controlSocket, hostName, portNum):
    """Connects the socket to the host and port, and 
    handles any exceptions"""
    try:
        controlSocket.connect((hostName, int(portNum)))
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED: #Handling the exception of the socket connection being refused
            print "error: socket connection refused"
            sys.exit(1)
        else:
            print "Error: a socket exception occured"
            sys.exit(1)

    print 'Sucessfully established TCP control connection\n'        

def sendHostPortCmd(controlSocket, cmd, dataPort):
    
    """Send the command to the server.
    exit the program if an invalid command is entered"""

    #send the command that the user passed in earlier as well as the data port number and host
    controlSocket.send(dataPort + ":" + cmd)    
    recieved = controlSocket.recv(1024)
    print recieved

    if 'valid' in recieved:

        dataSocket = createSocket() #Create data socket
        if 'list' == cmd:
            dataSocket.bind(('',int(dataPort)))
            dataSocket.listen(1)
            controlSocket.send("valid cmd received")
            while 1:
                connectionSocket, addr = dataSocket.accept()
                received = connectionSocket.recv(1024)
                print received + '\n'

            
        if 'get' in cmd:
            dataSocket.bind(('',dataPort))
            dataSocket.listen(1)
            while 1:
                connectionSocket, addr = dataSocket.accept()
                received = connectionSocket.recv(1024)
                print received + '\n'

    controlSocket.close()


#Main program---------------------------

#Get the hostname and port number
hostName, ctrlPort, dataPort, cmd = getHostPortCmd() 



#Make the socket for the client
controlSocket = createSocket() 

# connect the client socket
connectControlSocket(controlSocket, hostName, ctrlPort) 

#get the command from user input and send to the server, as well as the hostname and dataport number
sendHostPortCmd(controlSocket, cmd, dataPort) 



