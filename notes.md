# Overall architecture
The task is to take messages from an input file and process them and then returning them in the order they were received. If we processed them sequentially it would take approximately 1062.95 seconds to complete. Instead, I have setup a task-based processing system that processes the tasks in parallel, but still returns them in the same order. One of the challenges with parallel execution is that we need to write the processed results not in order of completion, but in order of receipt.

To accomplish this task I have used [Celery](http://www.celeryproject.org/) to manage the distributed worker processes. I then iterate over the messages, sending them to a Celery queue, and then as they are finished write them to the output file. Celery manages the asynchronous tasks and workers without much intervention. There are approaches I took, a minimal approach (solution 1) and an approach that more closely approximates the real world data generation process and architecture based on my reading of `record_rc.py` (solution 2)

Both solution's code is contained in the `stream_processor` package (in a folder with the same name in this repo).

## Solution 1
This solution reads the input file (`sampled_rc.json`) in line by line. On each line a task to process is sent to a Celery Queue. This stores the `AsyncResult` corresponding to each line in the input in a list in order. After all tasks are sent, it iterates over the results: checking if the 0th result is done yet, if it is, it `pop`s it from the list, writes it to the file and continues to iterate. This will write the results as soon as is feasible while still maintaining order.

This approach accomplishes the task in 95.43 seconds with 12 concurrent workers and 272.89 seconds with 4 concurrent workers.

This solution can be run by installing `stream_processor` (e.g. with `pip install ./stream_processor`) and then running `python run.py`. The core code for executing this is the `process_full_stream` function in `main.py`. The file `results_solution1.json` contains the output from running this.

## Solution 2
I wanted to expand on solution 1 by simulating the messages being sent over a SocketIO-based messaging system. For this, I had to build a SocketIO server using `python-socketIO` and `eventlet`. The server (in `socket_server.py`) sends the messages from `sampled_rc.json`. And the client (in `socket_client.py`) receives those messages. The client uses an instance of the class `StreamProcessor` (in `main_streaming.py`) to send messages received to a Celery queue, as well as keep track of the `AsyncResult`s in order, clearing that stack of results as they are done (again, ensuring that order is maintained).

This approach accomplishes the task in 105.93 seconds with 12 concurrent workers and 283.06 seconds with 4 concurrent workers.

This solution can be run by installing `stream_processor` (e.g. with `pip install ./stream_processor`) and then running `python run_streaming.py`. The core code for executing this is the `StreamProcessor` class and its methods in `main_streaming.py`. The file `results_solution2.json` contains the output from running this.

One additional feature of this solution is that it can be used to simulate receiving messages not just in the order they are in `sampled_rc.json`, but also approximately in the same temporal sequence (using the `timestamp` attribute of each message). This can be run by setting the `real_time_stream` variable at the top of `run_streaming.py` to `True`. This takes 318.99 seconds with 12 concurrent workers (19 seconds over the 5 minutes it takes to play the recording in real time, including some teardown overhead.)

# Possible complications and extensions
It is not explicitly stated in the prompt, but I'm assuming that the processing tasks for each message is independent of the processing of any other message. This allows naive parallelization like the approach here. If it were the case that there were dependencies between the processing steps, a more complicated parallelization would need to be implemented (though Celery has some features that would allow for this in some circumstances).

With more time and a better understanding of the failure states: I would add more exception handling and error-checking throughout.

# Dependencies
Written for Python 3 compatibility, thought it should be backwards compatible with Python 2.7. The only dependency that isn't pure Python and listed in `setup.py` is [RabbitMQ](https://www.rabbitmq.com/). This can be installed on MacOS with `brew install rabbitmq` or [other operating systems using RabbitMQ's instructions](https://www.rabbitmq.com/download.html).
