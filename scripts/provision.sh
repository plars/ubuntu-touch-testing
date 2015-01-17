#!/bin/bash

## This is the script jenkins should run to provision a device in the lab

set -e

BASEDIR=$(dirname $(readlink -f $0))
export PATH=${BASEDIR}/../utils/host:${PATH}

RESDIR=`pwd`/clientlogs
RECOVERY_URL="http://people.canonical.com/~plars/touch"

NETWORK_FILE="${NETWORK_FILE-${HOME}/.ubuntu-ci/wifi.conf}"

IMAGE_OPT="${IMAGE_OPT---bootstrap --developer-mode --channel ubuntu-touch/devel-proposed}"
UUID="${UUID-$(uuidgen -r)}"
PHABLET_PASSWORD="${PHABLET_PASSWORD-0000}"

usage() {
cat <<EOF
usage: $0 [-s ANDROID_SERIAL] [-n NETWORK_FILE] [-P ppa] [-p package] [-r revision] [-w]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -n    Select network file
  -P    add the ppa to the target (can be repeated)
  -D    add a debian package dir to the target (can be repeated)
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
	echo "$IMAGE_OPT" | grep -q "\-\-revision" || REVISION="--revision=${REV}"
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
	adb-shell sudo ntpdate 91.189.94.4 || log "WARNING: could not set ntpdate"
	# hwclock sync has to happen after we set writable image
	adb-shell sudo hwclock -w || log "WARNING: could not sync hwclock"
	log "Current date on device is:"
	adb shell date
	log "Current hwclock on device is:"
	adb shell sudo hwclock
}

retry() {
	timeout=$1
	shift
	loops=$1
	shift
	cmd=$*
	loopcnt=0
	while true; do
		$cmd && break || {
			if [ $loopcnt -lt $loops ] ; then
				loopcnt=$[$loopcnt+1]
				echo "Retry [$loopcnt/$loops] after $timeout seconds..."
				sleep $timeout
			else
				echo Failed on \'$cmd\' after $loops retries
				exit 1
			fi
		}
	done
}

reboot_bootloader() {
	# In CI, we've seen cases whre 'adb reboot bootloader' will just
	# reboot the device and not enter the bootloader. Adding another
	# reboot and retrying was found to be a successful workaround:
	# https://bugs.launchpad.net/ubuntu/+source/android-tools/+bug/1359488
	#
	# We only want to do this if we know ANDROID_SERIAL. Attempting
	# to guess might end up flashing the wrong device.

	log "Attempting adb reboot bootloader"
	adb reboot bootloader
	if [ -n "${ANDROID_SERIAL}" ] ; then
	       	# Entering the bootloader should take < 10 seconds, add some
		# padding for device variance.
		sleep 30
		if ! fastboot devices | grep -q "${ANDROID_SERIAL}"; then
			log "Device not in fastboot after adb reboot bootloader"
			# After a failed 'reboot bootloader' attempt, a reboot
			# is used to get the device back to a saner state.
			adb reboot
			return 1
		fi
	fi
	return 0
}

full_flash() {
	log "FLASHING DEVICE"
	DEVICE_TYPE=$(get-device-type)
	# Use a 60 second retry loop for reboot_bootloader.
	# If the attempt failed, it may take nearly 60 seconds to complete
	# the reboot cycle to get the device back to a sane state.
	retry 60 3 reboot_bootloader
	# Use a 10 second retry loop for ubuntu-device-flash.
	# Most failures appear to be transient and work with an immediate
	# retry.
	RECOVERY=""
	mkdir -p recovery
	wget -P recovery \
		${RECOVERY_URL}/recovery-${DEVICE_TYPE}.img || /bin/true
        if [ -f recovery/recovery-${DEVICE_TYPE}.img ]; then
		RECOVERY="--recovery-image=recovery/recovery-${DEVICE_TYPE}.img"
	fi
	retry 10 3 timeout 1800 ubuntu-device-flash ${REVISION} touch ${RECOVERY} --password $PHABLET_PASSWORD $IMAGE_OPT
	adb wait-for-device
	sleep 60  #give the system a little time
}

while getopts i:s:n:P:D:p:r:wh opt; do
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
	D)
		CUSTOMIZE="$CUSTOMIZE --package-dir $OPTARG"
		;;
	p)
		CUSTOMIZE="$CUSTOMIZE -p $OPTARG"
		;;
	r)
                REVISION="--revision=$OPTARG"
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
	full_flash
else
	log "CREATING EMULATOR"
	ubuntu-emulator destroy --yes $ANDROID_SERIAL || true
	sudo ubuntu-emulator create $ANDROID_SERIAL $IMAGE_OPT
	${BASEDIR}/reboot-and-wait
fi

if [ -z $USE_EMULATOR ] ; then
	log "SETTING UP WIFI"
	retry 60 5 adb-shell 'sudo -iu phablet env |grep UPSTART_SESSION=unix'
	retry 60 5 phablet-network -n $NETWORK_FILE
fi

phablet-config welcome-wizard --disable

if [ -n "$CUSTOMIZE" ] ; then
	log "CUSTOMIZING IMAGE"
	phablet-config writable-image -r ${PHABLET_PASSWORD} $CUSTOMIZE
fi

log "SETTING UP SUDO"
adb shell "echo ${PHABLET_PASSWORD} |sudo -S bash -c 'echo phablet ALL=\(ALL\) NOPASSWD: ALL > /etc/sudoers.d/phablet && chmod 600 /etc/sudoers.d/phablet'"

# FIXME: Can't do this through phablet-config for now because it needs auth
# phablet-config edges-intro --disable
adb shell "sudo dbus-send --system --print-reply --dest=org.freedesktop.Accounts /org/freedesktop/Accounts/User32011 org.freedesktop.DBus.Properties.Set string:com.canonical.unity.AccountsService string:demo-edges variant:boolean:false"

if [ -n "${SKIP_CLICK}" ]; then
	log "SKIPPING CLICK PACKAGE SETUP AS REQUESTED"
else
	log "SETTING UP CLICK PACKAGES"
	CLICK_TEST_OPTS=""
	channel_name=$(adb shell "sudo system-image-cli -i | sed -n -e 's/channel: \(.*\)/\1/p' | paste -s -d:")
	# Before running phablet-click-test setup, we need to make sure the
	# session is available
	retry 60 5 adb-shell 'sudo -iu phablet env |grep UPSTART_SESSION=unix'

	# FIXME: workaround for phablet-click-test-setup to pull the right sources
	if [[ $channel_name == *rtm* ]] ; then
		CLICK_TEST_OPTS="--distribution ubuntu-rtm --series 14.09"
	fi
	phablet-click-test-setup $CLICK_TEST_OPTS
fi

# get our target-based utilities into our PATH
adb push ${BASEDIR}/../utils/target /home/phablet/bin

image_info

set_hwclock
