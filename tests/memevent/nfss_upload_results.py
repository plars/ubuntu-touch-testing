#!/usr/bin/python3

"""This script takes a memevent-test result json and uploads any interesting
data contained within.

It will process any memory result files found in /tmp/ matching the naming
scheme: "/tmp/memory_usage_*.json"

"""

import json
import sys
import datetime
import subprocess
from glob import glob
import re
from requests_oauthlib import OAuth1Session

json_results_filename_pattern = "/tmp/memory_usage_*.json"


def _get_run_details(app_name):
    # Add extra details as per bootspeeds' run.py
    return dict(
        image_arch='',
        ran_at=datetime.datetime.utcnow().isoformat(),
        package_version=_get_package_version(app_name),
        application_name=app_name,
    )


def _get_app_details(app_name, json_data):
    """Given the json data extract out the details for each application
    contained within.

    incl. package version

    """

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

    print("...")
    print(run_json_string)
    print("...")
    # try:
    #     output = subprocess.check_output(
    #         ['./quick_upload.py', 'memevent', test_name, run_json_string]
    #     )
    # except subprocess.CalledProcessError as e:
    #     print("Unable to upload data: ", e)


def _get_app_name_from_filename(filename):
    "memory_usage_*.json"
    app_name_search = re.search('memory_usage_(.*)\.json', filename)
    return app_name_search.group(1)

if __name__ == '__main__':
    # target file is passed in
    # Open file and load json data
    # Create an entry for each application-name contained within the file
    # after all entries read, for each entry created upload the details to nfss
    # backend.

    for json_result_file in glob(json_results_filename_pattern):
        with open(json_result_file, "r") as f:
            json_data = json.load(f)
        app_name = _get_app_name_from_filename(json_result_file)
        run_details = _get_run_details(app_name)
        application_details = _get_app_details(app_name, json_data)

        upload_json_details(run_details, application_details)
