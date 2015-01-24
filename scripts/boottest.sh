#!/bin/bash
set -ex

# Where am I ?
BASEDIR=$(dirname $(readlink -f $0))/..

# The release to test the package on.
export RELEASE=${1:-vivid}
# The source package under test.
export SRC_PKG_NAME=${2:-libpng}
# The phone name.
export NODE_NAME=$3

# These can be set by jenkins when running in that context

# ANDROID_SERIAL: The phone ID.
export ANDROID_SERIAL=${ANDROID_SERIAL:-$(${BASEDIR}/scripts/get-adb-id ${NODE_NAME})}
# The package version to test
export VERSION=${VERSION:-whatever}


PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"
TEST_SOURCE=${BASEDIR}/tests/boottest

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# the archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Ensures we start with a usable phone
test-runner/scripts/recover.py ${NODE_NAME}

# Provision the device
# FIXME: workaround #82 being unbootable for krillin assuming we run on
# dev-jenkins until this is fixed -- vila 2015-01-23
REVISION="${REVISION:-81}"
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
    -r $REVISION \
	-n ${HOME}/.ubuntu-ci/wifi.conf -w

# Modify the debian changelog in boottest to show that it's testing the 
# package and version we care about
sed -e "s/{{ source_package }}/${SRC_PACKAGE_NAME}/" \
    -e "s/{{ package_version }}/${VERSION}/" \
    -e "s/{{ series }}/${RELEASE}/" \
    ${TEST_SOURCE}/debian/changelog.template > ${TEST_SOURCE}/debian/changelog

# Lookup the binary packages installed for the given source package
packages=$($BASEDIR/scripts/boottest.py -b ${SRC_PACKAGE_NAME})
echo $packages

# Generate the adt-run setup-command
rm -f adt-commands || true
echo "apt-get update" > adt-commands
echo "apt-get install -y ${packages}" >> adt-commands

# Now execute the test
# - from $TEST_SOURCE containing only the boottest dep8 test
# - setting up -proposed and doing apt-get update
# - via adt-virt-ssh with a setup from adb
# - pitti said to use '--apt-upgrade' but that fails on the phone
# (http://dev-jenkins.ubuntu-ci:8080/job/vila-bootesting/10/console)
adt-run --no-built-binaries --unbuilt-tree ${TEST_SOURCE} \
     -o results \
    --apt-pocket=proposed \
    --setup-commands=adt-commands \
    --- adt-virt-ssh -s /usr/share/autopkgtest/ssh-setup/adb \
    -- -s "${ANDROID_SERIAL}"
rc=$?

# XXX - fginther 20150123
# Outputting the result is meaningless but is here to facilitate development.
# Something like the run-autopkgtest script will extract the result from
# the adt-run results.
if [ "${rc}" ]; then
	echo "PASS"
else
	echo "FAIL"
fi


# Ensure we leave a usable phone
test-runner/scripts/recover.py ${NODE_NAME}

exit $rc
