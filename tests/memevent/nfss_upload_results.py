#!/usr/bin/python3

"""This script takes memevent-test result json filse and uploads the
interesting data contained within to a nfss backend.

It will process any memory result files found in /tmp/ matching the naming
scheme: "/tmp/memory_usage_*.json"

"""

import datetime
import json
import os
import re
import sys
import subprocess

from collections import defaultdict
from glob import glob

upload_script = ""
source_file_path = ""


def _get_run_details(app_name):
    # Add extra details as per bootspeeds' run.py
    return dict(
        image_arch='',
        ran_at=datetime.datetime.utcnow().isoformat(),
        package_version=_get_package_version(app_name),
        application_name=app_name,
    )


def _get_package_version(appname):
    """Return the package version for application *appname*.

    Return empty string if appname details are not found.

    """

    try:
        dpkg_output = subprocess.check_output(
            ['dpkg', '-s', appname],
            universal_newlines=True
        )
        version_line = [
            l for l in dpkg_output.split('\n') if l.startswith('Version:')
        ]
        return version_line[0].split()[1]
    except (subprocess.CalledProcessError, IndexError):
        return ""


def upload_json_details(run_details, app_details):
    app_run_details = run_details.copy()
    app_run_details["events"] = app_details

    _upload_data(run_details['application_name'], app_run_details)


def _upload_data(test_name, run_json):
    try:
        run_json_string = json.dumps(run_json)
    except ValueError as e:
        print("Error: Data does not appear to be valid json: %s" % e)
        sys.exit(3)

    print("Uploading data for :memevent:-", test_name)
    global upload_script
    try:
        upload_process = subprocess.Popen(
            [upload_script, 'memevent', test_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = upload_process.communicate(
            input=run_json_string.encode()
        )
        print("stdout: {}\n\nstderr: {}".format(stdout, stderr))
    except Exception as e:
        print("Something went terribly wrong: ", e)
    # try:
    #     output = subprocess.check_output(
    #         ['./quick_upload.py', 'memevent', test_name, run_json_string]
    #     )
    # except subprocess.CalledProcessError as e:
    #     print("Unable to upload data: ", e)


def _get_files_app_name_and_test(filename):
    """return tuple containing (appname, testname)."""
    app_name_search = re.search(
        'memory_usage_([a-zA-Z-]*).(.*)\.json',
        filename
    )
    return (app_name_search.group(1), app_name_search.group(2))


def get_application_readings(json_data):
    app_results = []
    pids = json_data["pids"]
    for reading in json_data["readings"]:
        results = dict(
            event=reading["event"],
            start_time=reading["start_time"],
            stop_time=reading["stop_time"],
        )
        # find the data results for this event (based on pid).
        for pid in pids:
            if str(pid) in reading["data"].keys():
                results["data"] = reading["data"][str(pid)]
                results["pid"] = pid
                break
        app_results.append(results)
    return app_results


def get_application_results(json_filepath):
    with open(json_filepath, "r") as f:
        json_data = json.load(f)
    return get_application_readings(json_data)


def get_application_details(application_files):
    """For every file this application has grab out the details and return a
    list dictionaries containing reading details.

    """
    app_result = []
    for json_file in application_files:
        app_result.extend(get_application_results(json_file))
    return app_result


def map_files_to_applications():
    """For any memory result files that exist, return a dictionary whos keys
    are the applications name mapped to the file.

    We can then produce a single json result for each application regardless of
    there being many tests / results for it.

    """

    global source_file_path
    json_results_filename_pattern = os.path.join(
        source_file_path,
        "memory_usage_*.json"
    )
    file_map = defaultdict(list)
    for json_result_file in glob(json_results_filename_pattern):
        app_name, test_name = _get_files_app_name_and_test(json_result_file)
        file_map[app_name].append(json_result_file)
    return file_map


def usage():
    print("{} <source file path> <nfss upload script>".format(sys.argv[0]))


def main():
    if len(sys.argv) != 3:
        usage()
        exit(1)

    global source_file_path
    source_file_path = sys.argv[1]

    global upload_script
    upload_script = sys.argv[2]

    app_details = dict()
    file_map = map_files_to_applications()
    for app_name in file_map.keys():
        app_details[app_name] = get_application_details(file_map[app_name])

    for app_name in app_details.keys():
        run_details = _get_run_details(app_name)
        upload_json_details(run_details, app_details[app_name])


if __name__ == '__main__':
    main()
