#!/bin/bash

## This is the script jenkins should run to provision a device in the lab

set -e

BASEDIR=$(dirname $(readlink -f $0))
export PATH=${BASEDIR}/../utils/host:${PATH}

RESDIR=`pwd`/clientlogs

NETWORK_FILE="${NETWORK_FILE-/home/ubuntu/magners-wifi}"

IMAGE_OPT="${IMAGE_OPT---bootstrap --developer-mode --channel ubuntu-touch/devel-proposed}"
UUID="${UUID-$(uuidgen -r)}"

usage() {
cat <<EOF
usage: $0 [-s ANDROID_SERIAL] [-n NETWORK_FILE] [-P ppa] [-p package] [-r revision] [-w]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -n    Select network file
  -P    add the ppa to the target (can be repeated)
  -p    add the package to the target (can be repeated)
  -r    Specify the image revision to flash
  -w    make the system writeable (implied with -p and -P arguments)

EOF
}

image_info() {
	# mark the version we installed in /home/phablet/.ci-[uuid,flash-args]
	# adb shell messes up \n's with \r\n's so do the whole of the regex on the target
	IMAGEVER=$(adb shell "sudo system-image-cli -i | sed -n -e 's/version version: \([0-9]*\)/\1/p' -e 's/version ubuntu: \([0-9]*\)/\1/p' -e 's/version device: \([0-9]*\)/\1/p' | paste -s -d:")
	CHAN=$(adb shell "sudo system-image-cli -i | sed -n -e 's/channel: \(.*\)/\1/p' | paste -s -d:")
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

set_hwclock() {
	log "SETTING HWCLOCK TO CURRENT TIME"
        # Use ip for ntp.ubuntu.com in case resolving doesn't work yet
	adb-shell ntpdate 91.189.94.4 || log "WARNING: could not set ntpdate"
	# hwclock sync has to happen after we set writable image
	adb-shell hwclock -w || log "WARNING: could not sync hwclock"
	log "Current date on device is:"
	adb shell date
	log "Current hwclock on device is:"
	adb shell hwclock
}

while getopts i:s:n:P:p:r:wh opt; do
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
	r)
		IMAGE_OPT="$IMAGE_OPT --revision $OPTARG"
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

if [ ! -f $NETWORK_FILE ] && [ -z $USE_EMULATOR ] ; then
	echo "ERROR: NETWORK_FILE, $NETWORK_FILE, not found"
	exit 1
fi

set -x
[ -d $RESDIR ] && rm -rf $RESDIR
mkdir -p $RESDIR

if [ -z $USE_EMULATOR ] ; then
	log "FLASHING DEVICE"
        if [ "${DEVICE_TYPE}" = "krillin" ]; then
		# reboot to recovery for krillin
		adb reboot recovery
                # Wait for recovery to boot
                sleep 30
        else
		adb reboot bootloader
	fi
	ubuntu-device-flash --password ubuntuci $IMAGE_OPT
	adb wait-for-device
	sleep 60  #give the system a little time
else
	log "CREATING EMULATOR"
	ubuntu-emulator destroy --yes $ANDROID_SERIAL || true
	sudo ubuntu-emulator create $ANDROID_SERIAL $IMAGE_OPT
	${BASEDIR}/reboot-and-wait
fi

if [ -z $USE_EMULATOR ] ; then
	log "SETTING UP WIFI"
	phablet-network -n $NETWORK_FILE
fi

phablet-config welcome-wizard --disable
# FIXME: Can't do this through phablet-config for now because it needs auth
# phablet-config edges-intro --disable
adb shell "dbus-send --system --print-reply --dest=org.freedesktop.Accounts /org/freedesktop/Accounts/User32011 org.freedesktop.DBus.Properties.Set string:com.canonical.unity.AccountsService string:demo-edges variant:boolean:false"

if [ -n "$CUSTOMIZE" ] ; then
	log "CUSTOMIZING IMAGE"
	phablet-config writable-image $CUSTOMIZE
fi

log "SETTING UP SUDO"
adb shell "echo ubuntuci |sudo -S bash -c 'echo phablet ALL=\(ALL\) NOPASSWD: ALL > /etc/sudoers.d/phablet && chmod 600 /etc/sudoers.d/phablet'"

log "SETTING UP CLICK PACKAGES"
phablet-click-test-setup

# get our target-based utilities into our PATH
adb push ${BASEDIR}/../utils/target /home/phablet/bin

image_info

set_hwclock
