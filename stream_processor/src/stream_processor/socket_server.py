import time, json
import socketio
import eventlet
import logging

def start_server(input_file):
    """ Initiate a socket server that simulates a server sending the change
    messages specified in the input.
    Keyword arguments:
    input_file -- line delimited JSON file with change messages
    """
    # create a Socket.IO server
    sio = socketio.Server()
    # wrap with a WSGI application
    app = socketio.WSGIApp(sio)

    def send_stream(input_file, realtime = False):
        """Send lines from input_file as if it were streaming
        Optionally use the timestamps in the messages to stream in realtime as
        opposed to all at once.

        Keyword arguments:
        input_file -- line delimited JSON file with change messages
        realtime -- should the messages be sent as if they were being streamed
        in realtime based on the timestamp of the message
        """
        # read messages
        messages = []
        with open(input_file) as f:
            for line in f:
                message = json.loads(line)
                messages.append(message)

        if realtime:
            # send messages by their timestamps
            current_time = time.time()
            # the difference between current time and the start time of the messages
            time_delta = current_time - messages[0]["timestamp"]
            end_time = messages[-1]["timestamp"]
            while len(messages) > 0:
                if messages[0]["timestamp"] <= current_time - time_delta:
                    current_message = messages.pop(0)
                    sio.emit("message", {"data": current_message})
                    sio.sleep(0.1)
                current_time = time.time()
        else:
            # send all of the messages in sequence
            while len(messages) > 0:
                current_message = messages.pop(0)
                sio.emit("message", {"data": current_message})
                sio.sleep(0.1)

    @sio.on("connect")
    def connect(sid, environ):
        print("connect", sid)

    @sio.on("disconnect")
    def disconnect(sid):
        print("disconnect", sid)

    @sio.on("start stream")
    def stream(sid, realtime):
        msg = "sending stream"
        if realtime:
            msg = msg + " in realtime"
        print(msg)
        send_stream(input_file, realtime)

    # start the server serving with eventlet
    eventlet.wsgi.server(eventlet.listen(("", 5000)),
                         app, 
                         log = logging.Logger("socket_server"))
