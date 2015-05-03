import time
import sys
import logging
from threading import Thread
import signal
import socket
import queue
import re

from zocp import ZOCP
import websocketserver
import httpserver


class ZOCPclient(ZOCP):
    # Constructor
    def __init__(self, nodename="", paramname="", fromsockets=None, tosockets=None):
        self.tosockets = tosockets
        self.fromsockets = fromsockets
        self.nodename = nodename
        self.paramname = paramname
        super().__init__()

    def run(self):
        self.set_node_name(self.nodename)
        self.register_string(self.paramname, '', 'rw')
        super().run()
                
    def on_modified(self, data, peer=None):
        if self._running and peer:
            modifiedkey = (list(data.keys())[0])
            if modifiedkey == self.paramname:
                value = "%s:%s" % (peer, data[self.paramname]['value'])
                self.tosockets.put(value.encode('utf-8').decode('latin-1'))

    def fromsocket_loop(self):
        self.loop_running = True
            
        while self.loop_running:
            while not fromsockets.empty():
                message = fromsockets.get()
                matches = re.match('^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}):(.*)$', message)
                if matches:
                    (nodeid,message) = matches.groups()
                    
                    encoded = message.encode('latin-1').decode('utf-8')
                    if not nodeid in self.get_capability():
                        self.register_string(nodeid, encoded, 'rw')
                    else:
                        self.capability[nodeid]['value'] = encoded
                        #self._on_modified(data=self.capability)
                else:
                    encoded = message.encode('latin-1').decode('utf-8')
                
                self.capability[self.paramname]['value'] = encoded
                self._on_modified(data=self.capability)
                

class CustomWebSocketServer(websocketserver.WebSocketServer):
    # Constructor
    def __init__(self, client, server, cls, fromsockets=None, tosockets=None):
        self.fromsockets = fromsockets
        self.tosockets = tosockets
        
        super().__init__(client, server, cls)
        
    def loop(self):
        super().loop()
        while not self.tosockets.empty():
            message = self.tosockets.get()
            self.broadcast_message(message)
    
        
    def broadcast_message(self, data):
        # send a message to all current connections
        for connection in self.connections:
            self.connections[connection].send_message(data)

        
class CustomWebSocket(websocketserver.WebSocket):
    def on_message(self, data):
        logging.info("Got message from %s: %s" % (self.client.fileno(), data))
        self.server.broadcast_message(data)
        self.server.fromsockets.put(data)
        
    def on_open(self):
        logging.info("Connection opened: %s" % self.client.fileno())
    
    def on_close(self):
        logging.info("Connection closed: %s" % self.client.fileno())
        
# Entry point
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    
    tosockets = queue.Queue()
    fromsockets = queue.Queue()
    
    http_server = httpserver.HTTPServer("", 8000, 'www')
    http_server_thread = Thread(target=http_server.listen)
    http_server_thread.start()
    
    socket_server = CustomWebSocketServer("", 8001, CustomWebSocket, fromsockets, tosockets)
    socket_server_thread = Thread(target=socket_server.listen, args=[5])
    socket_server_thread.start()
    
    zocp_client = ZOCPclient("websocket@"+socket.gethostname(), "Message", fromsockets, tosockets)
    zocp_client_thread = Thread(target=zocp_client.run)
    zocp_client_thread.start()
    
    fromsockets_loop_thread = Thread(target=zocp_client.fromsocket_loop)
    fromsockets_loop_thread.start()
    
    # Add SIGINT handler for killing the threads
    def signal_handler(signal, frame):
        logging.info("Caught Ctrl+C, shutting down...")
        zocp_client.loop_running = False
        zocp_client._running = False
        zocp_client.stop()
        socket_server.running = False
        http_server.close()
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        time.sleep(100)
