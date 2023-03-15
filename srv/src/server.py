from parser import InvalidEntryError, Parser
from additional_logic import additional_handler
from database import Query, get_entries
from googleapiclient.errors import HttpError

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from sys import argv


p = Parser()

class Server(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}).encode())
        
    # POST echoes the message adding a JSON field
    def do_POST(self): 
        j_header = self.headers.get_all("Content-Type")
        if not j_header or j_header[0] != "application/json":
            self.send_response(400)
            self.end_headers()
            return
        
        length = self.headers.get_all("Content-Length")
        if not length or not length[0].isnumeric():
            self.send_response(400)
            self.end_headers()
            return

        message = json.loads(self.rfile.read(int(length[0])))
        
        if not message.get("type"):
            self.send_response(400)
            self.end_headers()
            return
        if message.get("type") == "insert":
        # w = "cR tMAÑ10:30 ir al gimnasio"
            if not message.get("word"):
                self.send_response(400)
                self.end_headers()
                return
            try: 
                e = p.parse(message["word"])

                additional_handler(e) 

                res = {"parsed": e.to_dict()}
                self._set_headers()
                self.wfile.write(json.dumps(res).encode())
                return
            except InvalidEntryError as error:
                self._set_headers()
                self.wfile.write(json.dumps({"error": str(error), "type": "invalid_entry"}).encode())
                return
       
            except HttpError as error:
                self._set_headers()
                self.wfile.write(json.dumps({"error": error.reason, "type": "google_calendar"}).encode())
                

        elif message.get("type") == "query":
            if not (params := message.get("params")):
                self.send_response(400)
                self.end_headers()
                return
            
            q = Query(texto=params.get("texto"), timestamp=params.get("timestamp"))
            result = get_entries(q)     
            if result.error:
                self.send_response(401)
                self.end_headers()
                return
   
            self._set_headers()
            self.wfile.write(json.dumps({"result": result.results}).encode())
            return
             


def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    httpd.serve_forever()
    
if __name__ == "__main__":
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
