#!/bin/bash

## This is the script jenkins should run to provision a device in the lab

set -e

BASEDIR=$(dirname $(readlink -f $0))

RESDIR=`pwd`/clientlogs

NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

IMAGE_OPT="${IMAGE_OPT-ubuntu-system -b --channel ubuntu-touch/trusty-proposed}"
UUID="${UUID-$(uuidgen -r)}"

usage() {
cat <<EOF
usage: $0 [-s ANDROID_SERIAL] [-n NETWORK_FILE] [-P ppa] [-p package] [-w]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -n    Select network file
  -P    add the ppa to the target (can be repeated)
  -p    add the package to the target (can be repeated)
  -w    make the system writeable (implied with -p and -P arguments)

EOF
}

image_info() {
	# mark the version we installed in /home/phablet/.ci-[uuid,flash-args]
	# adb shell messes up \n's with \r\n's so do the whole of the regex on the target
	IMAGEVER=$(adb shell "system-image-cli -i | sed -n -e 's/version version: \([0-9]*\)/\1/p' -e 's/version ubuntu: \([0-9]*\)/\1/p' -e 's/version device: \([0-9]*\)/\1/p' | paste -s -d:")
	CHAN=$(adb shell "system-image-cli -i | sed -n -e 's/channel: \(.*\)/\1/p' | paste -s -d:")
	REV=$(echo $IMAGEVER | cut -d: -f1)
	echo "$IMAGE_OPT" | grep -q "\-\-revision" || IMAGE_OPT="${IMAGE_OPT} --revision $REV"
	echo "$IMAGE_OPT" | grep -q "\-\-channel" || IMAGE_OPT="${IMAGE_OPT} --channel $CHAN"
	adb shell "echo '${IMAGEVER}' > /home/phablet/.ci-version"
	echo $UUID > $RESDIR/.ci-uuid
	adb push $RESDIR/.ci-uuid /home/phablet/
	cat > $RESDIR/.ci-flash-args <<EOF
$IMAGE_OPT
EOF
	adb push $RESDIR/.ci-flash-args /home/phablet/.ci-flash-args
	echo $CUSTOMIZE > $RESDIR/.ci-customizations
	adb push $RESDIR/.ci-customizations /home/phablet/.ci-customizations
}

log() {
	echo = $(date): $*
}

while getopts i:s:n:P:p:wh opt; do
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
	i)
		IMAGE_TYPE=$OPTARG
		;;
	w)
		# making this a non-zero length string enables the logic
		CUSTOMIZE=" "
		;;
	P)
		CUSTOMIZE="$CUSTOMIZE --ppa $OPTARG"
		;;
	p)
		CUSTOMIZE="$CUSTOMIZE -p $OPTARG"
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

if [ ! -f $NETWORK_FILE ] ; then
	echo "ERROR: NETWORK_FILE, $NETWORK_FILE, not found"
	exit 1
fi

set -x
[ -d $RESDIR ] && rm -rf $RESDIR
mkdir -p $RESDIR

log "FLASHING DEVICE"
phablet-flash $IMAGE_OPT
adb wait-for-device
sleep 20  #give the system a little time

log "SETTING UP CLICK PACKAGES"
phablet-click-test-setup

log "SETTING UP WIFI"
phablet-network -n $NETWORK_FILE

if [ "$IMAGE_TYPE" = "touch_sf4p" ]; then
    adb shell rm -f /home/phablet/.display-mir
fi

phablet-config edges-intro --disable

# get our target-based utilities into our PATH
adb push ${BASEDIR}/../utils/target /home/phablet/bin

image_info

if [ -n "$CUSTOMIZE" ] ; then
	log "CUSTOMIZING IMAGE"
	phablet-config writable-image
        # Make sure whoopsie-upload-all can work (bug #1245524)
        adb shell "sed -i '/Waiting for whoopsie/ a\    subprocess.call([\"restart\", \"whoopsie\"])' /usr/share/apport/whoopsie-upload-all"
fi
