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
import signal


#functions
def sigIntHandler(signal, frame):
    """
    Function: sigIntHandler()

    Input Parameters:
        signal: the signal to write the handler for
        frame: the function which is the signal handler

    Output:
        Prints a message saying the server is exiting when the signal is received

    Description:
        A signal handler for the SIGINT signal. When the user presses CTRL-C while 
        the server is listening for commands from the client, the server will print
        a message saying it is exiting and invoke the exit function to exit the program.
        Invoking the exit function ensures that the kernel closes all the sockets

    Internal Dependencies:
        None

    External Dependencies:
        python sys API
    """

    print 'Server exiting...\n'
    sys.exit(0)

def getPort():
    """
    Function: getPort()

    Input Parameters: None

    Output:
        None, unless the arguments are entered incorrectly, then a message is printed showing how
        the arguments should be entered properly

    Description:
        parses the command line input for the control port number using getopt and returns it. Handles
        any exceptions from incorrect input
        
    Internal Dependencies:
        none

    External Dependencies:
        python getopt library
        
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as err:
        print "USAGE: ./ftserver.py -c [controlport] \n"
               
    ctrlPort = None

    for o, a in opts:
        if o == "-c":
            ctrlPort = a

    return ctrlPort

def createSocket():
    """
    Function: createSocket()

    Input Parameters:
        None

    Output:
        returns a TCP IPv4 socket, but if the creation of the socket fails,
        an error message is printed

    Description:
        Creates a TCP IPv4 socket, and handles any exceptions that occur by
        exiting

    Internal Dependencies:
        None

    External Dependencies:
        python socket API
        python sys API
    """

    
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    except socket.error:
        print "Error in socket creation"
        sys.exit(1)

def connectDataSocket(dataSocket, hostName, dataPort):
    """
    Function: connectDataSocket()

    Input Parameters: 
        the socket to connect to a particular hostname and port number (dataSocket)
        the hostname to connect the socket to (hostName)
        the port number to connect the socket to (dataPort)

    Output:
        error messages are printed if the socket connection is refused or if any other
        error happens

    Description:
        This function connects the socket used for the TCP data connection to
        the appropriate host name and port number for the data connection.

    Internal Dependencies: 
        None

    External Dependencies:
        python socket API
        python error library
        python sys API
    """


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
    """
    Function: checkCmd()

    Input Parameters:
        the socket used to send data over the TCP control connection (connectionSocket)
        the command sent to the server by the client (cmd)

    Output:
        None, nothing is returned

    Description:
        This function simply checks if the command sent by the client is a valid list or get command.
        For checking a get command, it is necessary to check if the command contains the string 'get '
        and that it is longer than 4 characters, to ensure that the command contains the word 'get' and
        the name of a file which is at least 1 character long. An appropriate message is sent to the 
        client depending on whether the command is valid or not.

    Internal Dependencies:
        None

    External Dependencies:
        python socket API
       
    """
    validCmd = False
    if 'list' == cmd:
        validCmd = True
 
    elif 'get ' in cmd and len(cmd) > 4:
        validCmd = True

    if validCmd == False:
        connectionSocket.send('Invalid command entered; Valid commands are \'list\', and \'get <filename>\'')
    else:
        connectionSocket.send('valid command sent: ' + cmd)

    return validCmd    

def execListCmd(dataSocket):
    """
    Function: execListCmd()
    
    Input Parameters:
        the socket used to send data over the TCP data connection (dataSocket)
        
    Output:
        Nothing is returned, the function simply prints to the server's screen a 
        message indicating that it is executing a list command

    Description:
        This function gets in list format all the files in the current directory
        of the server, and then it iterates through this list, and adds each filename
        on to a string, adding a newline character after each. After the list has been
        completely iterated through, the string contains the names of all the files in 
        the servers current directory, with a newline after each. Then, this string is
        sent to the client.

    Interal Dependencies:
        None

    External Dependencies:
        python socket API
        python os API
    """

    print 'Executing \'list\' command...\n'

    files = os.listdir(os.curdir)
    fileStr = ''

    for i in files:
          fileStr = fileStr + i + '\n'

    dataSocket.send(fileStr+"end")    

def execGetCmd(connectionSocket, dataSocket, cmd):
    """
    Function: execGetCmd()

    Input Parameters:
        the socket used to send data over the TCP control connection (connectionSocket)
        the socket used to send data over the TCP data connection (dataSocket)
        the command sent to the client from the server (cmd)

    Output:
        Nothing is returned, various messages are printed depicting the progress
        towards completing the get command, how many bytes have been sent, what file
        the client is requesting, and an error message is printed if the socket connection
        becomes broken.

    Description:
        This function executes the get command, and it is called by the listenForCmd() function.  
        It extracts the name of the file from the get command sent by the user, and then sees
        if the file exists on the servers current directory. If it doesn't, an error message is
        sent to the client. If it does, the client is sent the name of the file and its size.
        Once the client receives this information it sends back a message saying "transfer". When 
        the server receives this message, the file is opened in read mode on the server and sent to 
        the client in the while loop. 

    Internal Dependencies:
        None

    External Dependencies:
        python socket API
        python os API
        python sys API

    """
    fileName = cmd.split()[1]
    print 'Executing \'get\' ' + fileName + ' command...\n'

    fileSize = 0
                   
    try:
        fileSize = os.path.getsize(fileName)

    except os.error:
        connectionSocket.send('error: the file was not found')

    else:
        connectionSocket.send(fileName + ":" + str(fileSize))
        received = connectionSocket.recv(1024)
        if received == "transfer":

               #Start sending the file to the client here
               fileStr = open(fileName, 'r').read()
               totalBytesSent = 0
               while totalBytesSent < fileSize:
                       sent = dataSocket.send(fileStr[totalBytesSent:])

                       print "Bytes sent: " + str(sent) + " out of " + str(fileSize) + " \n" 

                       if sent == 0:
                            print 'Socket connection broken\n'
                            sys.exit(1)

                       totalBytesSent = totalBytesSent + sent                       


def listenForCmd(controlSocket,portNum,clientHostName):
    """
    Function: listenForCmd()

    Input parameters: 
        the Socket for the TCP control connection (controlSocket)
        the port number the TCP control socket should bind to (portNum)
        the host name of the client (clientHostName)

    Output:
        This function doesn't output anything except when there is an 
        invalid command given by the client, then it prints 'invalid command'
        on the screen

    Description:
        Waits for the command, data connection port, and client hostname to be 
        sent from the client, then checks if it is a valid command or not (using the
        checkCmd() function). If the command is valid, and the command was a list command,
        the execListCmd() function is invoked in order to list the contents of the current
        directory on the server and send them to the client. However if the user sent a get
        command, the execGetCmd() function is invoked to send the requested file to the 
        client if it exists on the server.

    Internal Dependencies:
        validCmd()
        execListCmd()
        execGetCmd()

    External Dependencies:
        python socket API
        python os API
        python sys API
        python signal API
    """
    controlSocket.bind(('',int(portNum)))
    controlSocket.listen(1)
    print 'Server is ready to recieve commands\n'

    #Register the signal handler
    signal.signal(signal.SIGINT, sigIntHandler)

    while 1:
        connectionSocket, addr = controlSocket.accept()
        received = connectionSocket.recv(1024)
        receivedArray = received.split(":")

        dataPort = receivedArray[0]
        cmd = receivedArray[1]
        clientHostName = receivedArray[2] 

        validCmd = checkCmd(connectionSocket, cmd)  #Check if the command sent was valid
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
                   execListCmd(dataSocket)

               elif 'get ' in cmd and len(cmd) > 4:
                   execGetCmd(connectionSocket, dataSocket, cmd)

           dataSocket.close()        
        connectionSocket.close()

#main program
ctrlPort = getPort() #get host and port numbers
controlSocket = createSocket() #create the socket for the TCP control connection
listenForCmd(controlSocket, ctrlPort, clientHostName) # Await user commands from the server
