#!/bin/bash
set -ex

# These are all set via jenkins when running in that context
if [ -z "${ANDROID_SERIAL}" ] || [ -z "${package_archive}" ] || \
	[ -z "${test_packages}" ] || [ -z "${test_suite}" ]; then
	echo "Missing an env variable: "
	echo "    ANDROID_SERIAL, package_archive, test_packages or test_suite"
	exit 1
fi

BASEDIR=$(dirname $(readlink -f $0))/..
ARCHIVE_TMP=$(mktemp -d)
trap 'rm -rf "${ARCHIVE_TMP}"' EXIT HUP INT TERM

wget -O "${ARCHIVE_TMP}/archive.zip" ${package_archive}
unzip "${ARCHIVE_TMP}/archive.zip" -d "${ARCHIVE_TMP}"
package_dir="${ARCHIVE_TMP}/archive"

# This is the list of packages to be installed from the archive
# It's manually generated and supplied via the lp:cupstream2distro-config
# configuration files when executed by jenkins.
package_list=""
for package in ${test_packages}; do
	package_list="-p ${package} ${package_list}"
done

# This is a list of test suites to execute. It's normally just one.
suite_list=""
for suite in ${test_suite}; do
	suite_list="-a ${suite} ${suite_list}"
done

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# a local archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Provision the device and run the test suite.
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
	-n ${HOME}/.ubuntu-ci/wifi.conf \
	-D ${package_dir} ${package_list}
${BASEDIR}/scripts/run-smoke -s ${ANDROID_SERIAL} -n ${suite_list}
