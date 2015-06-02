#!/usr/bin/python3

# A simple script that runs adt-run, and retries a certain number of times
# if it didn't succeed.
#
# To use: simply call this with all the adt-run arguments afterwards, including
# the adt-run call as well:
#
# ./scripts/run-adt.py adt-run --unbuilt-tree foo -o results .....

import io
import subprocess
import sys

# Number of times to run adt-run before giving up.
MAX_RUN_COUNT = 3

# adt-run exit codes we should re-run the adt-run call on:
RETRY_CODES = (16, 20)


def main():
    global MAX_RUN_COUNT
    global RETRY_CODES

    arguments = sys.argv[1:]
    for try_num in range(MAX_RUN_COUNT):
        stdout = io.BytesIO()
        stderr = io.BytesIO()
        process = subprocess.Popen(
            arguments,
            stdout=stdout,
            stderr=stderr,
        )
        returncode = process.wait()
        if returncode not in RETRY_CODES:
            break
    with open('adt-run-stdout', 'wb') as stdout_file:
        stdout_file.write(stdout.getvalue())
    with open('adt-run-stderr', 'wb') as stderr_file:
        stderr_file.write(stderr.getvalue())
    sys.exit(returncode)


if __name__ == '__main__':
    main()
