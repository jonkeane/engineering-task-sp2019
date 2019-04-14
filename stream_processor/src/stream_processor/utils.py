import filecmp
from multiprocessing import Process
from .celery_server import app

def start_celery(num_concurrent_workers = None, loglevel = "error"):
    """ Start the celery server

    Keyword arguments:
    num_concurrent_workers -- number of concurrent workers, None will use the
    Celery default (# of threads on the system)
    loglevel -- what level of logging should the celery process use
    """
    # start celery as a daemon
    # set up a deamon process to send the stream
    celery_argv = ["worker", "--loglevel={}".format(loglevel)]
    if num_concurrent_workers is not None:
        celery_argv.append("--concurrency={}".format(num_concurrent_workers))
    celery_proc = Process(target = app.worker_main, kwargs = {"argv": celery_argv})
    celery_proc.daemon = True
    celery_proc.start()

def compare_input_output(input_file, results_file):
    """ Compare inpute_file and results_file

    Keyword arguments:
    input_file -- the file being used as input (here: sampled_rc.json)
    results_file -- the file that was output
    """
    if filecmp.cmp(input_file, results_file):
        print("The input and output files match. Good work!")
    else:
        print("The input and output files do not match.")
