#!/bin/bash
set -ex

# These are all set via jenkins when running in that context
# input - json encoded file with the test input
# output - location to dump the test results
# proposed - apt source line for the proposed pocket
# test_source - bzr branch with the test source to execute with adt-run
if [ -z "${ANDROID_SERIAL}" ]; then
	echo "Missing 'ANDROID_SERIAL' env variable: "
	exit 1
fi
if [ -z "${package}" ]; then
	echo "Missing 'package' env variable: "
	exit 1
fi
if [ -z "${output}" ]; then
	echo "Missing 'output' env variable: "
	exit 1
fi
if [ -z "${test_source}" ]; then
	echo "Missing 'test_source' env variable: "
	exit 1
fi

PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"
BASEDIR=$(dirname $(readlink -f $0))/..

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# the archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Provision the device and run the test suite.
# FIXME: workaround #82 being unbootable for krillin assuming we run on
# dev-jenkins until this is fixed -- vila 2015-01-23
REVISION="${REVISION-81}"
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
    -r $REVISION \
	-n ${HOME}/.ubuntu-ci/wifi.conf -w

# Grab the test_source
rm -rf test_source_dir || true
bzr branch "${test_source}" test_source_dir

# Now execute the test
# - from the test_source_dir containing only the boottest dep8 test
# - setting up -proposed and doing apt-get update
# - via adt-virt-ssh with a setup from adb
# - pitti said to use '--apt-upgrade' but that fails on the phone
# (http://dev-jenkins.ubuntu-ci:8080/job/vila-bootesting/10/console)
adt-run --no-built-binaries --unbuilt-tree test_source_dir \
     -o results \
    --apt-pocket=proposed \
    --setup-commands='apt-get update' \
    --setup-commands='pwd' \
    --- adt-virt-ssh -s /usr/share/autopkgtest/ssh-setup/adb \
    -- -s "${ANDROID_SERIAL}"
rc=$?

out_file_name="FAIL"
if [ "${rc}" ]; then
	out_file_name="PASS"
fi
touch "${output}/${out_file_name}"

exit $rc
