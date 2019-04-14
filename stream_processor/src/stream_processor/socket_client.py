import time, sys, json
import socketio
from .main_streaming import StreamProcessor


class StreamReceiver(socketio.ClientNamespace):
    """ A class to receive messages via SocketIO
    When a new message is received, it is added to the queue to be processed.
    To clear the stack of results as they come in use the wait() method
    """
    def setup_processor(self, results_file):
        # set up our StreamProcessor instance
        self.stream_processor = StreamProcessor(results_file)

    def on_connect(self):
        print("Client connected to message server")
        pass

    def on_disconnect(self):
        print("Client disconnected to message server")
        self.stream_processor.teardown()
        pass

    def on_message(self, data):
        self.stream_processor.add_message(data['data'])
        self.stream_processor.send_pending_messages()

    def wait(self, timeout = 60*6, no_pending_results_timeout = 10):
        """ Wait and poll the results for this instance

        Keyword arguments:
        timeout -- seconds to wait while writing pending results (default: 6 minutes)
        no_pending_results_timeout -- seconds to wait while the results list is
        empty (default: 10 seconds)
        """
        timeout = time.time() + timeout
        last_time_zero = None
        while True:
            if len(self.stream_processor.pending_results) == 0:
                # only set last_time_zero if it's None
                if last_time_zero is None:
                    last_time_zero = time.time()
            else:
                last_time_zero = None

            if time.time() > timeout:
                print("Timeout reached")
                break

            if last_time_zero is not None and time.time() > last_time_zero + no_pending_results_timeout:
                print("No pending results timeout reached")
                break

            self.stream_processor.write_pending_results()
            time.sleep(0.1)
