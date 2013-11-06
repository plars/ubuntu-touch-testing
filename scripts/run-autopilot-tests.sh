#!/bin/sh

set -e

BASEDIR=$(dirname $(readlink -f $0))/..
RESDIR=`pwd`/clientlogs

export PATH=${BASEDIR}/utils/host:${PATH}
export TARGET_PREFIX=adb-shell


usage() {
	cat <<EOF
usage: $0 -a APP [-s ANDROID_SERIAL] [-Q] [-o results_dir] [-S]

Runs a set of autopilot tests on the target

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to test
  -a    The application to test (can be repeated)
  -o    Specify the directory to place results in.
        Default: $RESDIR
  -Q    "Quick" don't do a reboot of the device before/between testsuites.
  -S    Skip the system-settle tests that run before/after each testsuite.

EOF
}

log_error() {
	echo ERROR: $* >> ${RESDIR}/runner-errors.txt
}

system_settle() {
	[ -z $NOSETTLE ] || return 0

	label=$1
	odir=$2
	rc=0
	settle=${BASEDIR}/tests/systemsettle/systemsettle.sh
	{
		export UTAH_PROBE_DIR=${odir}  # needed for log file location
		timeout 120s $settle -c5 -d6 -p 97.5 -l $label || rc=1
		echo $rc > ${odir}/settle_${label}.rc
	} 2>&1 | tee ${odir}/settle_${label}.log

	if [ "$label" = "after" ] ; then
		${BASEDIR}/scripts/combine_results ${odir}
	fi
}

test_app() {
	app=$1

	odir=${RESDIR}/${app}
	[ -d $odir ] && rm -rf $odir
	mkdir -p $odir || return 1

	system_settle before $odir
	phablet-config autopilot --dbus-probe enable || \
		(log_error "autopilot dbus-probe enable"; return 1)

	NOSHELL=""
	[ "$app" = "unity8" ] && NOSHELL="-n"

	if adb-shell /home/phablet/bin/unlock_screen.sh ; then
		phablet-test-run \
			$NOSHELL \
			-o ${odir} \
			-a /var/crash -a /home/phablet/.cache/upstart \
			-v $app || true
	else
		log_error "screen unlock, skipping $app"
	fi
	system_settle after $odir
}

reboot_wait() {
	if [ -z $QUICK ] ; then
		${BASEDIR}/scripts/reboot-and-wait
		files="/var/crash/* /home/phablet/.cache/upstart/*.log"
		if ! adb shell rm -rf "$FILES" ; then
			log_error "unable to remove crash and log files, retrying"
			adb wait-for-device
			adb shell rm -rf "$FILES"
		fi
	else
		echo "SKIPPING phone reboot..."
	fi
}

grab_powerd() {
	echo "grabbing powerd cli locks..."
	adb shell powerd-cli active &
	PIDS="$!"
	adb shell powerd-cli display on &
	PIDS="$PIDS $!"
}

release_powerd() {
	if [ -n "$PIDS" ] ; then
		echo "killing child pids: $PIDS"
		for p in $PIDS ; do
			kill $p || true
		done
		PIDS=""
	fi
}

main() {
	# print the build date so the jenkins job can use it as the
	# build description
	BUILDID=$(adb shell cat /home/phablet/.ci-version)
	echo "= TOUCH IMAGE VERSION:$BUILDID"

	[ -d $RESDIR ] || mkdir -p $RESDIR

	set -x

	for app in $APPS ; do
		set +x
		echo "========================================================"
		echo "= testing $app"
		echo "========================================================"
		set -x
		reboot_wait

		grab_powerd

		if ! test_app $app ; then
			log_error "testing $app, retrying"
			# we sometimes see sporatic adb failures that seem to
			# related to MTP. This adds a retry for the test.
			# test_app only fails on a device error (not a test
			# case error)
			adb wait-for-device
			test_app $app
		fi

		release_powerd
	done
}

while getopts s:a:o:QSh opt; do
	case $opt in
	h)
		usage
		exit 0
		;;
	s)
		export ANDROID_SERIAL=$OPTARG
		;;
	o)
		RESDIR=$OPTARG
		;;
	a)
		APPS="$APPS $OPTARG"
		;;
	Q)
		QUICK=1
		;;
	S)
		NOSETTLE=1
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
if [ -z "$APPS" ] ; then
	echo "ERROR: No app specified"
	usage
	exit 1
fi

trap release_powerd TERM INT EXIT
main
