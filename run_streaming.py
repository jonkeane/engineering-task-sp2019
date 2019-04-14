import time, filecmp, os
import socketio
from multiprocessing import Process
from stream_processor.socket_server import start_server
from stream_processor.socket_client import StreamReceiver
from stream_processor.utils import start_celery, compare_input_output

input_file = "./sampled_rc.json"
results_file = "./results.json"
socket_uri = "http://localhost:5000"
real_time_stream = False

# delete any previous results
try:
    os.unlink(results_file)
    print("Removed any previous results_files.")
except FileNotFoundError:
    pass

start_celery()

print("Processing the stream...")
start = time.time()

# set up a deamon process to send the stream
p = Process(target = start_server, args = [input_file])
p.daemon = True
p.start()

# create a Socket.IO client
sio = socketio.Client()

# setup the StreamReceiver
stream_receiver = StreamReceiver("")
stream_receiver.setup_processor(results_file)
sio.register_namespace(stream_receiver)

# If the connection is refused, try again after a second
try:
    sio.connect(socket_uri)
except socketio.exceptions.ConnectionError:
    time.sleep(1)
    sio.connect(socket_uri)

# start the stream
sio.emit("start stream", real_time_stream)

# wait for pending results to finish
# or until there are no more pending messages
stream_receiver.wait()

sio.disconnect()

# # close the message server
# p.terminate()

end = time.time()
total_time = round(end-start, 2)
print("Finished, processing took {} seconds.".format(total_time))

compare_input_output(input_file, results_file)
