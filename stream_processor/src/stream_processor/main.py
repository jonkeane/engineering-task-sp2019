from .tasks import process
import json, time, sys

def process_full_stream(input_file, results_file):
    """Process the stream file

    Keyword arguments:
    input_file -- line delimited JSON file with changes
    results_file -- file to write processed changes to
    """
    # set up a results list to store the async result objects in
    results = []

    # iterate through the input file sending each line as a job to celery workers
    with open(input_file) as f:
        for line in f:
            message = json.loads(line)
            results.append(process.delay(message))

    # while there are results left, pop the 0th and write it only when it is
    # finished
    out_file = open(results_file, 'w')
    while len(results) > 0:
        if results[0].ready():
            # if the 0th result is ready, write it, then pop it from the stack
            result = results.pop(0)
            out_file.write(json.dumps(result.get())+'\n')

    out_file.close()
