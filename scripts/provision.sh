#!/bin/bash

## This is the script jenkins should run to provision a device in the lab

set -e

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs

UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"
NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

IMAGE_OPT="${IMAGE_OPT---ubuntu-bootstrap --skip-utah --developer-mode}"
UUID="${UUID-$(uuidgen -r)}"

usage() {
cat <<EOF
usage: $0 [-s ANDROID_SERIAL] [-n NETWORK_FILE] [-D]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -n    Select network file
  -D    Use a "cdimage-touch" ie developer image rather than an ubuntu-system

EOF
}

while getopts i:s:n:Dh opt; do
    case $opt in
    h)
        usage
        exit 0
        ;;
    n)
        NETWORK_FILE=$OPTARG
        ;;
    s)
	export ANDROID_SERIAL=$OPTARG
        ;;
    D)
        IMAGE_OPT=""
        ;;
    i)
        IMAGE_TYPE=$OPTARG
        ;;
  esac
done

if [ -z $ANDROID_SERIAL ] ; then
    # ensure we only have one device attached
    lines=$(adb devices | wc -l)
    if [ $lines -gt 3 ] ; then
        echo "ERROR: More than one device attached, please use -s option"
	echo
        usage
        exit 1
    fi
fi

set -x
rm -rf clientlogs
mkdir clientlogs

${UTAH_PHABLET_CMD} --results-dir ${RESDIR} --network-file=${NETWORK_FILE} ${IMAGE_OPT}

# mark the version we installed in /home/phablet/.ci-version
if [ -n "$IMAGE_OPT" ] ; then
    DEVICE_TYPE=$(adb shell "getprop ro.cm.device" |tr -d '\r')
    # adb shell messes up \n's with \r\n's so do the whole of the regex on the target
    IMAGEVER=$(adb shell "system-image-cli -i | sed -n -e 's/version version: \([0-9]*\)/\1/p' -e 's/version ubuntu: \([0-9]*\)/\1/p' -e 's/version device: \([0-9]*\)/\1/p' | paste -s -d:")
    CHAN=$(adb shell "system-image-cli -i | sed -n -e 's/channel: \(.*\)/\1/p' | paste -s -d:")
    REV=$(echo $IMAGEVER | cut -d: -f1)
    IMAGE_OPT="${IMAGE_OPT} --revision $REV"
    IMAGE_OPT="${IMAGE_OPT} --channel $CHAN"
else
    IMAGEVER=$(adb shell "cat /var/log/installer/media-info |sed 's/.*(\([0-9\.]*\))/\1/'")
fi
adb shell "echo '${IMAGEVER}' > /home/phablet/.ci-version"
echo $UUID > clientlogs/.ci-uuid
adb push clientlogs/.ci-uuid /home/phablet/
cat >clientlogs/.ci-utah-args <<EOF
$IMAGE_OPT
EOF
adb push clientlogs/.ci-utah-args /home/phablet/.ci-utah-args

# get our target-based utilities into our PATH
adb push ${BASEDIR}/../utils/target /home/phablet/bin

phablet-click-test-setup

if [ "$IMAGE_TYPE" == "ro" ]; then
    adb shell rm -f /home/phablet/.display-mir
elif [ "$IMAGE_TYPE" == "mir" ]; then
    adb shell touch /home/phablet/.display-mir
fi

# ensure the "edges intro" is disabled so that it doesn't cause noise
# in the system
adb shell dbus-send --system --print-reply --dest=org.freedesktop.Accounts /org/freedesktop/Accounts/User32011 org.freedesktop.DBus.Properties.Set string:com.canonical.unity.AccountsService string:demo-edges variant:boolean:false
