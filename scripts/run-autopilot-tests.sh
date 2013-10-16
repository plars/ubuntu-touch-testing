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

system_settle() {
	[ -z $NOSETTLE ] || return 0

	label=$1
	odir=$2
	rc=0
	settle=${BASEDIR}/tests/systemsettle/systemsettle.sh
	{
		export UTAH_PROBE_DIR=${odir}  # needed for log file location
		timeout 120s $settle -c5 -d2 -p 97.5 -l $label || rc=1
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
	mkdir -p $odir

	system_settle before $odir

	adb-shell /home/phablet/bin/unlock_screen.sh
	phablet-test-run \
		-o ${odir} \
		-a /var/crash -a /home/phablet/.cache/upstart \
		-v $app || true

	system_settle after $odir
}

reboot_wait() {
	if [ -z $QUICK ] ; then
		# get the phone in sane place
		adb reboot
		# sometimes reboot doesn't happen fast enough, so add a little
		# delay to help ensure its actually rebooted and we didn't just
		# connect back to the device before it rebooted
		adb wait-for-device
		sleep 5
		adb wait-for-device
		adb shell 'rm -rf /var/crash/* /home/phablet/.cache/upstart/*.log'
		phablet-network --skip-setup -t 90s
	else
		echo "SKIPPING phone reboot..."
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
		test_app $app
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

main
