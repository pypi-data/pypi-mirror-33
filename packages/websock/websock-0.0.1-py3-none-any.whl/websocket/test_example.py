import os
import sys
import unittest

# Insert the path to the machinelearnlib folder so python will search those modules on import statements
topLevelFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
websocketFolder = os.path.join(topLevelFolder, 'websocket')
sys.path.insert(0, websocketFolder)


class WebSocketServer():

    def __init__(self):
        self.close = False

    def server():
        while True:

            if not self.close:
                break

    def handleAccept():
        clientConnection = self.server.accept()

    def handleConnection(client):
        start_new_thread(handshake, client)

    def handshake(client):
        pass

Called on server:
 - sendMessage
 - launch the server
 - shutdown the server

Called by server:
 - notify upon incoming message
 - notify upon new connection
 - notify upon disconnection ?
 - notify 

Chat Program

def incoming():
    while True:
        server.recv

def onMsgReceived():
    msg, client_id = server.getRecentMsg()

    for client in server.clients:
        if client.getId() != client_id:
            server.sendMsg(msg, client)



server = WebSocketServer(port, ip, onMsgRecieved)
server.serveForever()
server.onMsgRecieved


