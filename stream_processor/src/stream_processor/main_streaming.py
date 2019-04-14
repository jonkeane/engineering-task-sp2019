from .tasks import process
import json, time, sys

class StreamProcessor:
    """ A class to process an incoming stream of messages
    Add a message to the list to be processed with add_message(message)
    Send all available messages to Celery workers to be processed with send_pending_messages()
    Write any pending results (in order) with write_pending_results()
    Finalize the output file with teardown()
    """
    def __init__(self, results_file):
        self.messages_to_process = []
        self.pending_results = []
        self.out_file = open(results_file, 'w')

    def add_message(self, message):
        """Add messages to the queue of messages to send"""
        self.messages_to_process.append(message)

    def send_pending_messages(self):
        """Send any pending messages to Celery queue and workers"""
        while len(self.messages_to_process) > 0:
            message = self.messages_to_process.pop(0)
            self.pending_results.append(process.delay(message))

    def write_pending_results(self):
        """Write any completed results from Celery workers in order"""
        while len(self.pending_results) > 0:
            time.sleep(0.01)
            # only if the 0th result is ready, write it, then pop it from the
            # stack then repeat until there are only pending messages left.
            if self.pending_results[0].ready():
                result = self.pending_results.pop(0)
                self.out_file.write(json.dumps(result.get())+'\n')

    def teardown(self):
        self.out_file.close()
