#!/bin/bash

## Puts an older build on the device
## Intersting environment variables that must be set:
##  ANDROID_SERIAL - specify another android device
##  NETWORK_FILE - specify an alternative network file
##  UPGRADE_FROM - the revision to upgrade from, eg -1

set -eux

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs

UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"
ANDROID_SERIAL="${ANDROID_SERIAL-015d1884b20c1c0f}"  #doanac's nexus7 at home
NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"
UPGRADE_FROM="${UPGRADE_FROM--1}"
CLIENT_LOGS="${CLIENT_LOGS-/tmp}"

echo "INSTALLING OLD BUILD..."
$UTAH_PHABLET_CMD -s $ANDROID_SERIAL \
	--ubuntu-bootstrap -r $UPGRADE_FROM \
	--network-file $NETWORK_FILE \
	--skip-utah \
	--pull /var/crash \
	--results-dir=${CLIENT_LOGS}
