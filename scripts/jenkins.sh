#!/bin/bash

## This is the script jenkins should run to execute various touch applications

set -e

BASEDIR=$(dirname $(readlink -f $0))/..

RESDIR=`pwd`/clientlogs
UTAHFILE=${RESDIR}/utah.yaml
UTAH_PHABLET_CMD="${UTAH_PHABLET_CMD-/usr/share/utah/examples/run_utah_phablet.py}"


usage() {
	cat <<EOF
usage: $0 -a APP [-s ANDROID_SERIAL] [-p FILE -p FILE ...]  [-T] [-Q]

Provisions the given device with the latest build

OPTIONS:
  -h	Show this message
  -s    Specify the serial of the device to install
  -a    The application under the "tests" directory to test
  -p    Extra file to pull from target (absolute path or relative to /home/phablet)
  -T    Run the utah test from the target instead of the host
  -Q    "Quick" don't do a reboot of the device before running the test

EOF
}

cleanup() {
	set +e
}

test_from_target() {
	# push the runlist over to the test
	adb push ${BASEDIR}/tests ${TESTSUITE_TARGET_BASE} &> /dev/null

	# provisioning puts scripts under /home/phablet/bin which is writeable
	# all types of images. that's not in the PATH and we are running tests
	# here in a way that requires a writeable system so:
	adb shell cp /home/phablet/bin/* /usr/local/bin/

	${UTAH_PHABLET_CMD} \
		--results-dir ${RESDIR} \
		--skip-install --skip-network --skip-utah \
		--pull /var/crash \
		--pull /home/phablet/.cache/upstart \
		$EXTRA_PULL \
		-l ${TESTSUITE_TARGET}/master.run
}

test_from_host() {
	export PATH=${BASEDIR}/utils/host:${PATH}

	# allow for certain commands to run from host/target
	# see unity8-autopilot/ts_control for example
	export TARGET_PREFIX=adb-shell

	[ -z $ANDROID_SERIAL ] || ADBOPTS="-s $ANDROID_SERIAL"

	sudo TARGET_PREFIX=$TARGET_PREFIX PATH="${PATH}" ${UTAH_PHABLET_CMD} \
		${ADBOPTS} \
		--from-host \
		--results-dir ${RESDIR} \
		--skip-install --skip-network --skip-utah \
		--pull /var/crash \
		--pull /home/phablet/.cache/upstart \
		$EXTRA_PULL \
		-l ${TESTSUITE_HOST}/master.run
}

main() {
	rm -rf clientlogs
	mkdir clientlogs

	# print the build date so the jenkins job can use it as the
	# build description
	adb pull /var/log/installer/media-info ${RESDIR}
	BUILDID=$(adb shell cat /home/phablet/.ci-version)
	echo "= TOUCH IMAGE VERSION:$BUILDID"

	adb shell "top -n1 -b" > ${RESDIR}/top.log

	set -x
	adb shell 'rm -f /var/crash/*'
	if [ -z $QUICK ] ; then
		# get the phone in sane place
		adb reboot
		# sometimes reboot doesn't happen fast enough, so add a little
		# delay to help ensure its actually rebooted and we didn't just
		# connect back to the device before it rebooted
		adb wait-for-device
		sleep 5
		adb wait-for-device
		phablet-network --skip-setup
	else
		echo "SKIPPING phone reboot..."
	fi

	if [ ! -z $FROM_TARGET ] ; then
		echo "launching test on the target...."
		test_from_target
	else
		echo "launching test from the host...."
		test_from_host
	fi
	adb shell 'rm -f /var/crash/*'

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
}

while getopts p:s:a:TQh opt; do
    case $opt in
    h)
        usage
        exit 0
        ;;
    s)
        export ANDROID_SERIAL=$OPTARG
        ;;
    a)
        APP=$OPTARG
        ;;
	p)
		EXTRA_PULL_FILE=$OPTARG

		if [ ! -z $EXTRA_PULL_FILE ]; then
			# relative paths are assumed to be relative to /home/phablet
			E_P_START=`echo $EXTRA_PULL_FILE | cut -c1`

			if [ $E_P_START = '/' ]; then
				EXTRA_PULL="$EXTRA_PULL --pull $EXTRA_PULL_FILE"
			else
				EXTRA_PULL="$EXTRA_PULL --pull /home/phablet/$EXTRA_PULL_FILE"
			fi
		fi
		;;
    Q)
        QUICK=1
        ;;
    T)
        FROM_TARGET=1
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
if [ -z $APP ] ; then
    echo "ERROR: No app specified"
    usage
    exit 1
fi

TESTSUITE_HOST=$(readlink -f ${BASEDIR}/tests/${APP})
TESTSUITE_TARGET_BASE=/tmp/tests
TESTSUITE_TARGET=${TESTSUITE_TARGET_BASE}/$(basename ${TESTSUITE_HOST})

trap cleanup TERM INT EXIT
main
