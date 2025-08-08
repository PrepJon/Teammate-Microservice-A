import zmq
import json
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Example request
request = {"city": "Pittsburgh", }
socket.send_string(json.dumps(request))

reply = socket.recv_json()
print("Received reply:", reply)

time.sleep(5)

request = {"city": "Detroit", "units": "metric"}
socket.send_string(json.dumps(request))

reply = socket.recv_json()
print("Received reply:", reply)