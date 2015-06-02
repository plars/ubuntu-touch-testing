#!/usr/bin/python3

# A simple script that runs adt-run, and retries a certain number of times
# if it didn't succeed.
#
# To use: simply call this with all the adt-run arguments afterwards, including
# the adt-run call as well:
#
# ./scripts/run-adt.py adt-run --unbuilt-tree foo -o results .....

import subprocess
import sys

# Number of times to run adt-run before giving up.
MAX_RUN_COUNT = 3

# adt-run exit codes we should re-run the adt-run call on:
RETRY_CODES = (16, 20)


def main():
    arguments = sys.argv[1:]
    for _ in range(MAX_RUN_COUNT):
        with open('adt-run-stdout', 'wb') as stdout_file, \
        open('adt-run-stderr', 'wb') as stderr_file:
            process = subprocess.Popen(
                arguments,
                stdout=stdout_file,
                stderr=stderr_file,
            )
            returncode = process.wait()
            if returncode not in RETRY_CODES:
                break
    sys.exit(returncode)


if __name__ == '__main__':
    main()
