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
# Default adt-run timeout
export ADT_TIMEOUT=${ADT_TIMEOUT:-600}

# XXX psivaa 20150130: This is to use /var/local/boottest
# directory in tachash for rsyncing the results back.
# This should be revisited and fixed when the actual directory
# is decided for final
# May need tweaking/ removing the boottest section of /etc/rsyncd.conf
# in tachash
export RSYNC_DEST=${RSYNC_DEST:-rsync://tachash.ubuntu-ci/boottest/}


# Create an exit handler so that we are sure to create a error file even
# when the unexpected occurs.
function exit_handler {
# The errfile and resultfile variables can be used to determine if the
# exit was normal. If either exists, it's a normal exit, so don't overwrite
# the original errfile or resultfile.
if [ -z ${errfile} ] && [ -z ${resultfile} ]; then
    errfile=${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).error
    echo "$RELEASE $ARCH $SRC_PKG_NAME" > $errfile
    [ -f "$errfile" ] && rsync -a $errfile $RSYNC_DEST/${RELEASE}/tmp/ || true
fi

# Ensure we leave a usable phone
[ -z ${NODE_NAME} ] || test-runner/scripts/recover.py ${NODE_NAME}
}
trap exit_handler SIGINT SIGTERM EXIT

# If the NODE_NAME is unset, we're running locally, the commands that
# requires a phone are prefixed with "[ -z ${NODE_NAME} ] ||"
# If you have a phone available locally, set ANDROID_SERIAL and NODE_NAME=yes

# These can be set by jenkins when running in that context

# ANDROID_SERIAL: The phone ID.
[ -z ${NODE_NAME} ] || export ANDROID_SERIAL=${ANDROID_SERIAL:-$(${BASEDIR}/scripts/get-adb-id ${NODE_NAME})}
# The package version to test
export VERSION=${VERSION:-1.2.51-0ubuntu3}

BOOTTESTRC=${HOME}/.ubuntu-ci/boottest.rc
if [ -f $BOOTTESTRC ]; then
	source $BOOTTESTRC
fi

# FIXME: Should be provided -- vila 2015-01-26
ARCH="${ARCH:-krillin}"

PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"

# The provision.sh and run-smoke scripts can install extra packages to meet
# the needs of image testing. Since we are installing specific packages from
# the archive, this needs to be disabled.
export SKIP_CLICK=1
export SKIP_TESTCONFIG=1

# Ensures we start with a usable phone
[ -z ${NODE_NAME} ] || ${BASEDIR}/scripts/recover.py ${NODE_NAME}

TESTS=${BASEDIR}/tests

# Provision the device
# Allow the image revision to be overridden if the latest is unusable
REVISION="${REVISION:-0}"
PROV_CMD="${BASEDIR}/scripts/provision.sh \
    -r $REVISION \
    -n ${HOME}/.ubuntu-ci/wifi.conf -w"
[ -z ${NODE_NAME} ] || ${PROV_CMD} -s ${ANDROID_SERIAL}

# Generate the adt-run setup-command
rm -f adt-commands || true
# apt-get update like adt-run does it
echo "(apt-get update || (sleep 15; apt-get update))" >> adt-commands


# --no-built-binaries should come first
# --debug helps while debugging, can be removed otherwise
ADT_CMD="timeout ${ADT_TIMEOUT} adt-run --debug --no-built-binaries"
# ADT_VIRT can be overridden for local tests, 
# it defaults to ${ANDROID_SERIAL} phone via the adb/ssh combo
ADT_VIRT=${ADT_VIRT:-adt-virt-ssh -s /usr/share/autopkgtest/ssh-setup/adb \
    -- -s "${ANDROID_SERIAL}"}
# - setting up -proposed and doing apt-get update
# - via adt-virt-ssh with a setup from adb
# - using --apt-upgrade to ensure we only deal with packages already on the
#   phone (see above)
ADT_OPTS="--apt-pocket=proposed\
    --setup-commands=adt-commands \
    --- ${ADT_VIRT}"


# Inject the package name into getpkgsrc DEP8 test
FROM=${TESTS}/getpkgsrc/debian/tests/getpkgsrc.template
TARGET=${TESTS}/getpkgsrc/debian/tests/getpkgsrc
sed -e "s/{{ source_package }}/${SRC_PKG_NAME}/" ${FROM} > ${TARGET}

# Execute a first test to get the package source tree from the testbed.
PKG_SRC_DIR=pkgsrc
rm -fr ${PKG_SRC_DIR} || true
set +e
${ADT_CMD} --unbuilt-tree ${TESTS}/getpkgsrc -o ${PKG_SRC_DIR} ${ADT_OPTS}
RET=$?
set -e
if [ $RET -ne 0 ]; then
    # Something went wrong with the testbed and/or adt-run itself
    errfile=${PKG_SRC_DIR}/${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).error
    echo "$RELEASE $ARCH $SRC_PKG_NAME" > $errfile
    [ -f "$errfile" ] && rsync -a $errfile $RSYNC_DEST/${RELEASE}/tmp/ || true
    # Ensure we leave a usable phone
    [ -z ${NODE_NAME} ] || test-runner/scripts/recover.py ${NODE_NAME}

    exit $RET
fi

if [ -n "${FORCE_FAILURE}" ]; then
	# Force a boottest failure by running an alternate DEP8 test
	set +e
	${ADT_CMD} --unbuilt-tree ${TESTS}/bootfail -o results ${ADT_OPTS}
	RET=$?
	set -e
else
	# Inject the boot DEP8 test into the package source tree
	SOURCE_DIR=$(ls -d ${PKG_SRC_DIR}/artifacts/${SRC_PKG_NAME}-*)
	FROM=${TESTS}/boottest/debian/tests
	TARGET="${SOURCE_DIR}/debian/tests"
	mkdir -p ${TARGET} # For packages that don't define DEP8 tests
        # Inject the binary packages built previously
        BIN_PACKAGES=$(tr '\n' ',' < ${PKG_SRC_DIR}/artifacts/needs_install.packages | sed -e s/,$//)
        sed -e "s/{{ bin_packages }}/${BIN_PACKAGES}/" \
            ${FROM}/control.template > ${TARGET}/control
	cp ${FROM}/boottest ${TARGET}

	# Now execute the boot test from inside the pkg source tree
	set +e
	${ADT_CMD} --unbuilt-tree ${SOURCE_DIR} -o results ${ADT_OPTS}
	RET=$?
	set -e
fi

# Return Skipped as Passed
[ $RET -eq 2 ] && RET=0

if [ -e "results/testpkg-version" -a -e "results/testbed-packages" ]; then
    result='PASS'
    resultfile=results/${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).result
    [ $RET -gt 0 ] && result="FAIL"
    set +x  # quiet mode as it pollutes output
    echo "$RELEASE $ARCH $(cat results/testpkg-version) $result $(sort -u results/*-packages|tr -s '[\n\t]' ' ')" > $resultfile
    [ -f "$resultfile" ] && rsync -a $resultfile $RSYNC_DEST/${RELEASE}/tmp/ || true
else
    # Something went wrong with the testbed
    errfile=results/${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).error
    echo "$RELEASE $ARCH $SRC_PKG_NAME" > $errfile
    [ -f "$errfile" ] && rsync -a $errfile $RSYNC_DEST/${RELEASE}/tmp/ || true
fi

exit $RET
