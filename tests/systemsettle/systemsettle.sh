#!/bin/bash

# Configuration variables:
#  TARGET_PREFIX - Allows this to be run from the host, by providings something
#                  like TARGET_PREFIX="adb shell"
#  UTAH_PROBE_DIR - optionally where to save log files so utah will grab them

set -e

[ -z $UTAH_PROBE_DIR ] && UTAH_PROBE_DIR="/tmp"

# default exit code storage
dump_error=1

calc () { awk "BEGIN{ print $* }" ;}

function show_usage() {
   echo "Usage:"
   echo " $0 [options]"
   echo "Options:"
   echo " -r  run forever without exiting"
   echo " -p  minimum idle percent to wait for (Default: 99)"
   echo " -c  number of times to run top at each iteration (Default: 10)"
   echo " -d  seconds to delay between each top iteration (Default: 6)"
   echo " -i  top measurements to ignore from each loop (Default: 1)"
   echo " -m  maximum loops of top before giving up if minimum idle"
   echo "     percent is not reached (Default: 10)"
   echo " -l  label to include for the top_log file"
   exit 129
}

while getopts "h?rp:c:d:i:m:l:" opt; do
    case "$opt" in
        h|\?) show_usage
              ;;
        r)    settle_prefix='-'
              ;;
        p)    idle_avg_min=$OPTARG
              ;;
        c)    top_repeat=$OPTARG
              ;;
        d)    top_wait=$OPTARG
              ;;
        i)    top_ignore=$OPTARG
              ;;
        m)    settle_max=$OPTARG
              ;;
        l)    top_log_label=$OPTARG
              ;;
    esac
done

# minimum average idle level required to succeed
idle_avg_min=${idle_avg_min:-99}
# measurement details: top $top_wait $top_repeat
top_repeat=${top_repeat:-10}
top_wait=${top_wait:-6}
# how many samples to ignore
top_ignore=${top_ignore:-1}
# how many total attempts to settle the system
settle_max=${settle_max:-10}

top_log="$UTAH_PROBE_DIR/top$top_log_label.log"

# set and calc more runtime values
top_tail=`calc $top_repeat - $top_ignore`
settle_count=0
idle_avg=0

echo "System Settle run - quiesce the system"
echo "--------------------------------------"
echo
echo "  idle_avg_min   = '$idle_avg_min'"
echo "  top_repeat  = '$top_repeat'"
echo "  top_wait    = '$top_wait'"
echo "  top_ignore  = '$top_ignore'"
echo "  settle_max     = '$settle_max'"
echo "  run_forever    = '$settle_prefix' (- = yes)"
echo "  log files   = $top_log $top_log.reduced"
echo

while test `calc $idle_avg '<' $idle_avg_min` = 1 -a "$settle_prefix$settle_count" -lt "$settle_max"; do
  echo -n "Starting system idle measurement (run: $settle_count) ... "

  # get top
  echo "TOP DUMP (after settle run: $settle_count)" >> $top_log
  echo "========================" >> $top_log
  ${TARGET_PREFIX} top -c -b -d $top_wait -n $top_repeat >> $top_log
  cat $top_log | grep '.Cpu.*' | tail -n $top_tail > $top_log.reduced
  echo >> $top_log

  # calc average of idle field for this measurement
  sum=0
  count=0
  while read line; do
     idle=`echo $line | sed -e 's/.* \([0-9\.]*\) id.*/\1/'`
     sum=`calc $sum + $idle`
     count=`calc $count + 1`
  done < $top_log.reduced

  idle_avg=`calc $sum / $count`
  settle_count=`calc $settle_count + 1`

  echo " DONE."
  echo
  echo "Measurement:"
  echo "  + idle level: $idle_avg"
  echo "  + idle sum: $sum / count: $count"
  echo
done

if test `calc $idle_avg '<' $idle_avg_min` = 1; then
  echo "system not settled. FAIL"
  exit 1
else
  echo "system settled. SUCCESS"
  exit 0
fi

