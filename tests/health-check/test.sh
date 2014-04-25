#!/bin/sh

procname=$1
RC=0

pidline=$(cat /tmp/healthcheck/procmapping.txt | grep $procname:)
sed -i "/$pidline/d" /tmp/healthcheck/procmapping.txt
pid=$(echo $pidline | awk -F: '{print $NF}')

echo "Testing $procname - $pid"
/tmp/healthcheck/health-check-test-pid.py $pid
RC=$?

cp *.json /tmp/results
exit $RC
