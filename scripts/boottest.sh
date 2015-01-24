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
export VERSION=${VERSION:-1.2.51-0ubuntu3}


PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# the archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Ensures we start with a usable phone
test-runner/scripts/recover.py ${NODE_NAME}

TESTS=${BASEDIR}/tests

# Provision the device
# FIXME: workaround #82 being unbootable for krillin assuming we run on
# dev-jenkins until this is fixed -- vila 2015-01-23
REVISION="${REVISION:-81}"
${BASEDIR}/scripts/provision.sh -s ${ANDROID_SERIAL} \
    -r $REVISION \
	-n ${HOME}/.ubuntu-ci/wifi.conf -w

# Generate the adt-run setup-command
rm -f adt-commands || true
# FIXME: '-proposed' will be setup by adt-run but we still need one apt-get
# update call (vila -> pitti: why ?) -- vila 2015-01-24
echo "apt-get update" > adt-commands


# --no-built-binaries should come first
ADT_CMD="adt-run --no-built-binaries"
# - setting up -proposed and doing apt-get update
# - via adt-virt-ssh with a setup from adb
# - pitti said to use '--apt-upgrade' but that fails on the phone
# (http://dev-jenkins.ubuntu-ci:8080/job/vila-bootesting/10/console)
ADT_OPTS= --apt-pocket=proposed \
    --setup-commands=adt-commands \
    --- adt-virt-ssh -s /usr/share/autopkgtest/ssh-setup/adb \
    -- -s "${ANDROID_SERIAL}"

# Execute a first test to get the package source tree from the testbed.
PKG_SRC_DIR=${BASEDIR}/APT-GET-SOURCE
rm -fr ${PKG_SRC_DIR} || true
${ADT_CMD} --unbuilt-tree ${TESTS}/get-pkg-src -o ${PKG_SRC_DIR}

# Inject the boot DEP8 test into the package source tree
SOURCE_DIR=="${PKG_SRC_DIR}/${SRC_PKG_NAME}*"
FROM=${TESTS}/boottest/debian/tests
TARGET="${SOURCE_DIR}*/debian/tests"
mkdir -p ${TARGET} # For packages that don't define DEP8 tests
cp ${FROM}/control ${FROM}/boottest ${TARGET}

# Now execute the boot test from inside the pkg source tree
adt-run --no-built-binaries --unbuilt-tree ${SOURCE_DIR} \
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
