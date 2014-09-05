#!/bin/sh

set -e

cleanup()
{
	stop whoopsie || true
	rm -f /var/crash/_bin_sleep.0.*
	start whoopsie
}

if [ ! -e /var/lib/apport/autoreport ]; then
    echo "Automatic crash reporting not enabled."
    exit 1
fi

if [ -e /var/crash/_bin_sleep.0.crash ] || [ -e /var/crash/_bin_sleep.0.upload ] \
   || [ -e /var/crash/_bin_sleep.0.uploaded ]
then
	echo "Error: existing crash data found on disk.  Did a previous run fail?"
	exit 1
fi

trap cleanup 0 2 3 5 10 13 15

echo "Configuring whoopsie for staging"
stop whoopsie
if ! start whoopsie CRASH_DB_URL=https://daisy.staging.ubuntu.com
then
	echo "Failed to start whoopsie"
	exit 1
fi

sleep 10 &
echo "Background process id $!"
ps $!
echo "Sending SIGSEGV"
kill -SEGV $!

echo "Polling for .crash file"
crash_found=false
for i in $(seq 0 99); do
	if [ -e /var/crash/_bin_sleep.0.crash ]; then
		echo "Crash file created after $(($i*2)) seconds."
		crash_found=:
		break
	fi
	sleep 2
done
if ! $crash_found; then
	echo "whoopsie failed to create crash file within 200 seconds."
	exit 1
fi

echo "Polling for .upload file"
upload_found=false
for i in $(seq 0 19); do
	if [ -e /var/crash/_bin_sleep.0.upload ]; then
		echo "Upload file created after $i seconds."
		upload_found=:
		break
	fi
	sleep 1
done
if ! $upload_found; then
	echo "whoopsie_upload_all failed to run within 20 seconds."
	exit 1
fi

echo "Polling for .uploaded file"
uploaded_found=false
for i in $(seq 0 79); do
	if [ -e /var/crash/_bin_sleep.0.uploaded ]; then
		echo ".uploaded file created after $(($i*5)) seconds."
		uploaded_found=:
		break
	fi
	sleep 5
done
if ! $uploaded_found; then
	echo "whoopsie failed to upload crash file within 400 seconds."
	exit 1
fi

echo "crash file successfully uploaded."
exit 0
