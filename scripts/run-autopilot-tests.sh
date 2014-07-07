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

setup_test() {
	app=$1
	label=$2
	odir=$3
	{
		pkgs=$(${BASEDIR}/jenkins/testconfig.py packages -a $app)
		if [ "$label" = "setup" ] ; then
			adb-shell sudo apt-get install -yq --force-yes $pkgs
		else
			#Always remove dbus-x11 because it causes
			#problems when we leave it around
			pkgs="$pkgs dbus-x11"
			adb-shell sudo apt-get autoremove --purge -y $pkgs \
				|| /bin/true
		fi
		echo $? > ${odir}/setup_${label}.rc
	} 2>&1 | tee ${odir}/setup_${label}.log
}

system_settle() {
	[ -z $NOSETTLE ] || return 0

	label=$1
	odir=$2
	rc=0
	timeout=120s
	if [ "$label" = "before" ] ; then
		timeout=300s
	fi

	settle=${BASEDIR}/tests/systemsettle/systemsettle.sh
	{
		export UTAH_PROBE_DIR=${odir}  # needed for log file location
		timeout $timeout $settle -c5 -d6 -p 97.5 -l $label || rc=1
		echo $rc > ${odir}/settle_${label}.rc
	} 2>&1 | tee ${odir}/settle_${label}.log
}

test_app() {
	app=$1

	odir=${RESDIR}/${app}
	[ -d $odir ] && rm -rf $odir
	mkdir -p $odir || return 1

	system_settle before $odir
	phablet-config autopilot --dbus-probe enable || \
		(log_error "'autopilot dbus-probe enable' failed"; return 1)

	setup_test $app setup $odir

	NOSHELL=""
	[ "$app" = "unity8" ] && NOSHELL="-n"
	EXTRA=""
        # Use --timeout-profile=long only if we are using the emulator
	[ -z $USE_EMULATOR ] || EXTRA="-A '--timeout-profile=long'"

	phablet-test-run \
		$NOSHELL $EXTRA \
		-o ${odir} -f subunit \
		-a /var/crash -a /home/phablet/.cache/upstart \
                -a /var/log/syslog -a /var/log/kern.log \
		-v $app || true

	system_settle after $odir
	setup_test $app teardown $odir
	if [ -f ${odir}/test_results.subunit ] ; then
		cat ${odir}/test_results.subunit | subunit2junitxml > ${odir}/test_results.xml
	fi
	${BASEDIR}/scripts/combine_results ${odir}
}

reboot_wait() {
	if [ -z $QUICK ] ; then
		reboot-and-unlock.sh
		FILES="/var/crash/* /home/phablet/.cache/upstart/*.log*"
		if ! adb shell "sudo rm -rf $FILES" ; then
			log_error "unable to remove crash and log files, retrying"
			adb wait-for-device
			adb shell "sudo rm -rf $FILES"
		fi
	else
		echo "SKIPPING phone reboot..."
	fi
}

if [ -z $USE_EMULATOR ] ; then
grab_powerd() {
	echo "grabbing powerd cli locks..."
	adb shell sudo powerd-cli active &
	PIDS="$!"
	adb shell sudo powerd-cli display on &
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

else
grab_powerd() {
	#emulator does not use powerd, so this is noop
	return 0
}

release_powerd() {
	#emulator does not use powerd, so this is noop
	return 0
}
fi

dashboard_update() {
	# only try and update the dashboard if we are configured to
	[ -z $DASHBOARD_KEY ] && return 0
	[ -z $DASHBOARD_BUILD ] && return 0
	[ -z $DASHBOARD_IMAGE ] && return 0
	${BASEDIR}/scripts/dashboard.py $* \
		--image $DASHBOARD_IMAGE \
		--build $DASHBOARD_BUILD || true
}

dashboard_result_running() {
	dashboard_update result-running --test $1
}

dashboard_result_syncing() {
	xunit=${RESDIR}/${app}/test_results.xml
	[ -f $xunit ] || return 0

	# save a utah.yaml version of the results so the dashboard can process
	cat $xunit | ${BASEDIR}/scripts/junit2utah.py > ${RESDIR}/${app}/utah.yaml
	dashboard_update result-syncing --test $1 --results ${RESDIR}/${app}/utah.yaml
}

main() {
	[ -d $RESDIR ] || mkdir -p $RESDIR

	set -x

	for app in $APPS ; do
		set +x
		echo "========================================================"
		echo "= testing $app"
		echo "========================================================"
		set -x
		dashboard_result_running $app
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
		dashboard_result_syncing $app

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
if [ -n "$USE_EMULATOR" ] ; then
	echo "disabling system-settle testing for emulator"
	NOSETTLE=1
fi
main
