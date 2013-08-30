#!/bin/bash
# Run tests on ubuntu-touch devices and gather the results
# Set $RUNLIST to the runlist you wish to run
set -x

BRANCH=lp:~canonical-platform-qa/ubuntu-test-runlists/touch-runlists
WORKSPACE=/home/phablet/workspace
RESDIR=`pwd`/clientlogs
UTAHFILE=${RESDIR}/utah.yaml
UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"

function show_usage() {
    echo "USAGE: $0 -s ANDROID_SERIAL -r RUNLIST"
    echo "     -p - List of additional files/dirs to pull from target"
    exit 0
}

while getopts "h?p:r:s:" opt; do
    case "$opt" in
    h|\?)
        show_usage
        ;;
    p)  PULL_LIST=$OPTARG
        ;;
    r)  RUNLIST=$OPTARG
        ;;
    s)  ANDROID_SERIAL=$OPTARG
        ;;
    esac
done
if [ -z $ANDROID_SERIAL ]; then show_usage; fi

if [ -n "$PULL_LIST" ]; then
    PULL="--pull $PULL_LIST"
fi

if [ -z $QUICK ]; then
    adb -s $ANDROID_SERIAL reboot
    adb -s $ANDROID_SERIAL wait-for-device
    sleep 5
    adb -s $ANDROID_SERIAL wait-for-device
    phablet-network -s ${ANDROID_SERIAL} --skip-setup
else
    echo "SKIPPING phone reboot..."
fi
rm -rf ${RESDIR}
mkdir -p ${RESDIR}
adb -s ${ANDROID_SERIAL} pull /var/log/installer/media-info ${RESDIR}
BUILDID=`cat ${RESDIR}/media-info | awk '{ print $(NF)}' | sed -e 's/(//' -e 's/)//'`
echo "= TOUCH BUILD DATE:$BUILDID"

${UTAH_PHABLET_CMD} \
    -s ${ANDROID_SERIAL} \
    --results-dir ${RESDIR} \
    --skip-install --skip-network --skip-utah \
    ${PULL} \
    -l ${RUNLIST}

if ! `grep "^errors: [!0]" < $UTAHFILE >/dev/null` ; then
    echo "errors found"
    exit 1
fi
if ! `grep "^failures: [!0]" < $UTAHFILE >/dev/null` ; then
    echo "failures found"
    exit 2
fi
