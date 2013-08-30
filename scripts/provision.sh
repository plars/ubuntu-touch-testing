#!/bin/bash

## This is the script jenkins should run to provision a device in the lab
## Intersting environment variables that must be set:
##  ANDROID_SERIAL - specify another android device
##  NETWORK_FILE - an alternative network file if you aren't in the lab
##  TOUCH_IMAGE=--ubuntu-bootstrap   (provision with read-only system image)

set -e
set -x

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs
UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"

ANDROID_SERIAL="${ANDROID_SERIAL-015d1884b20c1c0f}"  #doanac's nexus7 at home
NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

rm -rf clientlogs
mkdir clientlogs

${UTAH_PHABLET_CMD} -s ${ANDROID_SERIAL} --results-dir ${RESDIR} --network-file=${NETWORK_FILE} ${TOUCH_IMAGE}

# get our target-based utilities into our PATH
adb -s ${ANDROID_SERIAL} push ${BASEDIR}/../utils/target /usr/local/bin/
