#!/bin/bash
set -ex

# These are all set via jenkins when running in that context
if [ -z "${ANDROID_SERIAL}" ] || [ -z "${proposed}" ] || \
	[ -z "${test_packages}" ]; then
	echo "Missing an env variable: "
	echo "    ANDROID_SERIAL, proposed or test_packages"
	exit 1
fi

PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"
BASEDIR=$(dirname $(readlink -f $0))/..

# This is the list of packages to be installed from the archive
# It's manually generated and supplied via the lp:cupstream2distro-config
# configuration files when executed by jenkins.
package_list=""
for package in ${test_packages}; do
	package_list="--package ${package} ${package_list}"
done

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# a local archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Provision the device and run the test suite.
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
	-n ${HOME}/.ubuntu-ci/wifi.conf -w

adb shell "sudo echo ${proposed} >> /etc/apt/souces.list"
adb shell "sudo apt-get update"
phablet-config writable-image -r ${PHABLET_PASSWORD} ${package_list}

# Now reboot the device
${BASEDIR}/reboot-and-wait

# Do something to make sure it is alive
adb shell "ls"
