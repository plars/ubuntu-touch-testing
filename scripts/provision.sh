#!/bin/bash

## This is the script jenkins should run to provision a device in the lab

set -e

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs

UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"
NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

IMAGE_OPT="--ubuntu-bootstrap"

usage() {
cat <<EOF
usage: $0 -s ANDROID_SERIAL [-n NETWORK_FILE] [-D]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -n    Select network file
  -D    Use a "cdimage-touch" ie developer image rather than an ubuntu-system

EOF
}

while getopts s:n:Dh opt; do
    case $opt in
    h)
        usage
        exit 0
        ;;
    n)
        NETWORK_FILE=$OPTARG
        ;;
    s)
        ANDROID_SERIAL=$OPTARG
        ;;
    D)
        IMAGE_OPT=""
        ;;
  esac
done

if [ -z $ANDROID_SERIAL ] ; then
    echo "ERROR: No android serial specified"
    usage
    exit 1
fi

set -x
rm -rf clientlogs
mkdir clientlogs

${UTAH_PHABLET_CMD} -s ${ANDROID_SERIAL} --results-dir ${RESDIR} --network-file=${NETWORK_FILE} ${IMAGE_OPT}

# mark the version we installed in /home/phablet/.ci-version
if [ -n "$IMAGE_OPT" ] ; then
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
