
# CS3251-A Sockets - Programming Assignment 2
##### 11/24/2016

~~~~
_______          _________ _       
(  ____ \|\     /|\__   __/( \      
| (    \/| )   ( |   ) (   | (      
| (__    | |   | |   | |   | |      
|  __)   ( (   ) )   | |   | |      
| (       \ \_/ /    | |   | |      
| (____/\  \   /  ___) (___| (____/\
(_______/   \_/   \_______/(_______/
~~~~

## Team:
    John Blum : jblum@gatech.edu
    Robert Smith : robertsmith@gatech.edu






## Files Included:

 * Evil.py - Evil socket implementation

 * connection.py - Evil connection implementation

 * util.py - provides various utilities for the other parts of the EVIL protocol,
    specifically it allows for selective debug text and handles parsing packets to and from strings

 * FTA-client - an example application using the EVIL protocol to do file transfer, client application

 * FTA-server - an example application using the EVIL protocol to do file transfer, server application

 * sampleOutput.txt - an example run of the program 


## Build and Run Instructions:
First, in one docker container determine the ip using ifconfig, remember this for later

now run the server using the python 2.x version, type the following into the terminal

    python FTA-server.py  5005 

next, in a second docker window, run

    python FTA-client.py (serverIP) 5005
*instead of (serverIP), type the ip found in part one using ifconfig*

note: port 5005 (or whatever your chosn port) must be available on the server container or EVIL will not be able to bind, so ensure that it is available.

## Features and Limits

- **Multiple clients & servers** allowed, as well as multiple connections per socket

- **FTA-client.post :** fta client can give files to the server, as well as get them

- *Requesting transfer of a file larger than available memory is not supported*
