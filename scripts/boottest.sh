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
if [ -z "${package}"]; then
	echo "Missing 'package' env variable: "
	exit 1
fi
if [ -z "${output}"]; then
	echo "Missing 'output' env variable: "
	exit 1
fi
if [ -z "${proposed}"]; then
	echo "Missing 'proposed' env variable: "
	exit 1
fi
if [ -z "${test_source}"]; then
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
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
	-n ${HOME}/.ubuntu-ci/wifi.conf -w

# Setup proposed-migration on the test device
rm -rf proposed.list || true
echo "deb ${proposed}" > proposed.list
echo "deb-src ${proposed}" >> proposed.list
adb push proposed.list /tmp
adb shell "sudo cp /tmp/proposed.list /etc/apt/sources.list.d/"
adb shell "sudo apt-get update"

phablet-config writable-image -r ${PHABLET_PASSWORD} --package ${package}

# Grab the test_source
rm -rf test_source_dir || true
bzr branch "${test_source}" test_source_dir

# Now execute the test
adt-run --unbuilt-tree test_source_dir --no-built-binaries -o test_logs --- ssh -s /usr/share/autopkgtest/ssh-setup/adb -- -s "${ANDROID_SERIAL}"
rc=$?

out_file_name="FAIL"
if [ "${rc}" ]; then
	out_file_name="PASS"
fi
touch "${output}/${out_file_name}"

exit $rc
