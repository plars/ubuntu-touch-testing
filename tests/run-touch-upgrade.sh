#!/bin/bash

## This is the script jenkins should run to test upgrading a system image
## in the lab.
## Intersting environment variables that must be set:
##  ANDROID_SERIAL - specify another android device
##  RUNLIST - the path the runlist
##  NETWORK_FILE - specify an alternative network file (passed to runlist)
##  UPGRADE_FROM - the revision to upgrade from, eg -1 (passed to runlist)

set -eux

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs

UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"
RUNLIST=${RUNLIST-"`pwd`/smoke-touch-apps/upgrade/master.run"}
ANDROID_SERIAL="${ANDROID_SERIAL-015d1884b20c1c0f}"  #doanac's nexus7 at home
NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

rm -rf clientlogs
mkdir clientlogs

export ANDROID_SERIAL=$ANDROID_SERIAL

set +e
sudo NETWORK_FILE=$NETWORK_FILE \
	$UTAH_PHABLET_CMD -s $ANDROID_SERIAL \
	--from-host --skip-install --skip-utah --skip-network  -l $RUNLIST \
	--results-dir=$RESDIR
EXITCODE=$?

UTAHFILE=$RESDIR/utah.yaml
if ! `grep "^errors: [!0]" < $UTAHFILE >/dev/null` ; then
  echo "errors found"
  EXITCODE=1
fi
if ! `grep "^failures: [!0]" < $UTAHFILE >/dev/null` ; then
  echo "failures found"
  EXITCODE=2
fi
echo "Results Summary"
echo "---------------"
egrep '^(errors|failures|passes|fetch_errors):' $UTAHFILE
exit $EXITCODE
