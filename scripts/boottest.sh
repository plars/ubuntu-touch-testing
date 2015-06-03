#!/bin/bash
set -e

# Where am I ?
BASEDIR=$(dirname $(readlink -f $0))/..

# Provide a message to report special information
END_MESSAGE=""

# The release to test the package on.
export RELEASE=${1:-vivid}
# The source package under test.
export SRC_PKG_NAME=${2:-libpng}
# The phone name.
export NODE_NAME=$3

# Default values can be provided via a local rc file (see
# ../config/boottest.rc.example).
BOOTTESTRC=${HOME}/.ubuntu-ci/boottest.rc
if [ -f $BOOTTESTRC ]; then
    source $BOOTTESTRC
fi

# Default adt-run timeout
export ADT_TIMEOUT=${ADT_TIMEOUT:-600}

# rsync can be disabled for local testing by defining:
# export RSYNC="echo rsync"
export RSYNC=${RSYNC:-rsync}
# XXX psivaa 20150130: This is to use /var/local/boottest
# directory in tachash for rsyncing the results back.
# This should be revisited and fixed when the actual directory
# is decided for final
# May need tweaking/ removing the boottest section of /etc/rsyncd.conf
# in tachash
export RSYNC_DEST=${RSYNC_DEST:-rsync://tachash.ubuntu-ci/boottest/}

# Look for a known bug, lp1421009, that results in unity8 not starting
# and prevents adt-run from accepting the testbed
check_for_lp1421009() {
    SYMPTOM="ERROR: timed out waiting for Unity greeter"
    LINK="http://launchpad.net/bugs/1421009"
    if [ $1 -eq 16 ] && grep -q "${SYMPTOM}" ${2}/log; then
        END_MESSAGE="Test failed due to ${LINK}"
    fi
}

# Create an exit handler so that we are sure to create a error file even
# when the unexpected occurs.
exit_handler() {
    # The errfile and resultfile variables can be used to determine if the
    # exit was normal. If either exists, it's a normal exit, so don't overwrite
    # the original errfile or resultfile.
    if [ -z ${errfile} ] && [ -z ${resultfile} ]; then
        errfile=${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).error
        echo "$RELEASE $ARCH $SRC_PKG_NAME" > $errfile
        [ -f "$errfile" ] && ${RSYNC} -a $errfile $RSYNC_DEST/${RELEASE}/tmp/ || true
    fi

    # Ensure we leave a usable phone
    [ -z ${NODE_NAME} ] || ${BASEDIR}/scripts/recover.py ${NODE_NAME}

    # Leave a parting message
    # (disable command tracing as it confuses the output)
    [ -z "${END_MESSAGE}" ] || echo -e "\n\n${END_MESSAGE}\n\n"
}
trap exit_handler SIGINT SIGTERM EXIT

# If the NODE_NAME is unset, we're running locally, the commands that
# requires a phone are prefixed with "[ -z ${NODE_NAME} ] ||"
# If you have a phone available locally, set ANDROID_SERIAL and NODE_NAME=yes

# These can be set by jenkins when running in that context

# ANDROID_SERIAL: The phone ID.
[ -z ${NODE_NAME} ] || export ANDROID_SERIAL=${ANDROID_SERIAL:-$(${BASEDIR}/scripts/get-adb-id ${NODE_NAME})}

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
RETRY=3
if [ -n "${NODE_NAME}" ]; then
    while [ ${RETRY} -gt 0 ]; do
        echo "Provisioning device"
        ${PROV_CMD} && break
        PROV_ERR=$?
        # Make sure the device doesn't need to be recovered first
        ${BASEDIR}/scripts/recover.py ${NODE_NAME}
        if [ ${PROV_ERR} -eq 124 ]; then
            # The provisioning fails with a timeout, the image is not
            # flashable/bootable
            echo ERROR: Device provisioning failed!
            END_MESSAGE="Test failed because the image couldn't be flashed/booted"
            exit 1
        fi
        RETRY=$((${RETRY}-1))
        echo "Provisioning failed, retrying up to ${RETRY} more times..."
    done
    if [ ${RETRY} -eq 0 ]; then
        echo ERROR: Device provisioning failed!
        exit 1
    fi
fi

# Generate the adt-run setup-command
rm -f adt-commands || true
# apt-get update like adt-run does it
echo "(apt-get update || (sleep 15; apt-get update))" >> adt-commands
# We need dctrl-tools installed so we can use grep-aptavail below
echo "apt-get install -f dctrl-tools" >> adt-commands
echo 'dpkg-query -f "\${binary:Package}\n" -W | sed -e "s/:.*$//" > installed.packages' >> adt-commands
echo "grep-aptavail -X -n -S -sPackage ${SRC_PKG_NAME}| sort | uniq > binary.packages" >> adt-commands
echo "comm  -1 -2 binary.packages installed.packages > needs_install.packages" >> adt-commands
echo 'release=$(lsb_release -s -c)' >> adt-commands
echo 'cat needs_install.packages | xargs apt-get install -f -t ${release}-proposed 2> apt-get-install.stderr' >> adt-commands
# The sourcepkg-version file contains the version of the first binary in the
# list of binaries to install. This version data is passed back to britney
# via the final .result file. Britney uses this to determine if the package
# that was tested matches the version requested.
# An assumption is made that this binary package version matches the other
# packages installed for this test. This works because the 'apt-get install'
# command is all or nothing. So all packages have either been updated to the
# new version or are all stuck at the original version.
echo 'head -n 1 needs_install.packages | xargs dpkg-query --show --showformat=\${Version} > /home/phablet/sourcepkg-version' >> adt-commands


# --no-built-binaries should come first
# --debug helps while debugging, can be removed otherwise
# 'timeout' returns 124 if ${ADT_TIMEOUT} is reached.
ADT_CMD=${ADT_CMD:-timeout ${ADT_TIMEOUT} adt-run --debug --no-built-binaries}
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


if [ -n "${FORCE_FAILURE}" ]; then
    # Force a boottest failure by running an alternate DEP8 test
    set +e
    echo "Running bootfail test suite."
    ${ADT_CMD} --unbuilt-tree ${TESTS}/bootfail -o results ${ADT_OPTS}
    RET=$?
    set -e
else
    # Now execute the boot test
    set +e
    echo "Running boottest test suite."
    ${BASEDIR}/scripts/run-adt.py ${ADT_CMD} --unbuilt-tree ${TESTS}/boottest -o results ${ADT_OPTS}
    RET=$?
    # Fetch the sourcepkg-version file that contains the version data
    # for the package under test. We can't use the testpkg-version file
    # that adt-run generates because it provides the version of the
    # fake boottest package, not the package we're actually testing.
    adb pull /home/phablet/sourcepkg-version results/sourcepkg-version
    set -e
fi

check_for_lp1421009 $RET results

# Return Skipped as Passed
[ $RET -eq 2 ] && RET=0

if [ -e "results/sourcepkg-version" -a -e "results/testbed-packages" ]; then
    result='PASS'
    resultfile=results/${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).result
    [ $RET -gt 0 ] && result="FAIL"
    echo "$RELEASE $ARCH ${SRC_PKG_NAME} $(cat results/sourcepkg-version) $result $(sort -u results/*-packages|tr -s '[\n\t]' ' ')" > $resultfile
    [ -f "$resultfile" ] && ${RSYNC} -a $resultfile $RSYNC_DEST/${RELEASE}/tmp/ || true
else
    # Something went wrong with the testbed
    errfile=results/${RELEASE}_${ARCH}_${SRC_PKG_NAME}_$(date +%Y%m%d-%H%M%S).error
    echo "$RELEASE $ARCH $SRC_PKG_NAME" > $errfile
    [ -f "$errfile" ] && ${RSYNC} -a $errfile $RSYNC_DEST/${RELEASE}/tmp/ || true
fi

exit $RET
