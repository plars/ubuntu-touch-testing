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

# mark the version we installed in /home/phablet/.ci-version
if [ -n "$TOUCH_IMAGE" ]; then
    DEVICE_TYPE=$(adb -s ${ANDROID_SERIAL} shell "getprop ro.cm.device" |tr -d '\r')
    bzr export si-utils lp:~ubuntu-system-image/ubuntu-system-image/server/utils
    IMAGEVER=$(si-utils/check-latest ${DEVICE_TYPE} |sed -n 's/Current full image: \([0-9]*\).*ubuntu=\([0-9\.]*\),.*=\([0-9\.]*\))/\1:\2:\3/p')
    rm -rf si-utils
else
    IMAGEVER=$(adb -s ${ANDROID_SERIAL} shell "cat /var/log/installer/media-info |sed 's/.*(\([0-9\.]*\))/\1/'")
fi
adb -s ${ANDROID_SERIAL} shell "echo '${IMAGEVER}' > /home/phablet/.ci-version"

# get our target-based utilities into our PATH
adb -s ${ANDROID_SERIAL} push ${BASEDIR}/../utils/target /home/phablet/bin

# ensure the "edges intro" is disabled so that it doesn't cause noise
# in the system
adb -s ${ANDROID_SERIAL} shell dbus-send --system --print-reply --dest=org.freedesktop.Accounts /org/freedesktop/Accounts/User32011 org.freedesktop.DBus.Properties.Set string:com.canonical.unity.AccountsService string:demo-edges variant:boolean:false
