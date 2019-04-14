import time, filecmp, os
from stream_processor.main import process_full_stream
from stream_processor.utils import start_celery, compare_input_output

# configuration
input_file = "./sampled_rc.json"
results_file = "./results.json"

# delete any previous results
try:
    os.unlink(results_file)
    print("Removed any previous results_files.")
except FileNotFoundError:
    pass

start_celery()
print("Processing the file...")

start = time.time()

# process the stream
process_full_stream(input_file, results_file)

end = time.time()
total_time = round(end-start, 2)
print("Finished, processing took {} seconds.".format(total_time))

compare_input_output(input_file, results_file)
