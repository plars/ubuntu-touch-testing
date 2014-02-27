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
   echo " -s  sleep timeout for %cpu calculation (Default: 10)"
   exit 129
}

while getopts "h?rp:c:d:i:m:l:s:" opt; do
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
        s)    sleep_len=$OPTARG
              ;;
    esac
done

sleep_len=${sleep_len:-10}
HZ=`getconf CLK_TCK`
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
  ${TARGET_PREFIX} COLUMNS=900 top -c -b -d $top_wait -n $top_repeat >> $top_log
  cat $top_log | grep '.Cpu.*' | tail -n $top_tail > $top_log.reduced
  echo >> $top_log

  # Instead of using top, we need to use /proc/stat and compensate for
  # the number of cpus and any frequency scaling that could be in effect
  cpu_avg=$({
    cat /proc/stat
    sleep "$sleep_len"
    cat /proc/stat
  } | awk '
    BEGIN       { iter = 0 }
    /^cpu /     { iter = iter + 1; count = 0; next }
    /^cpu/      { S[iter] = S[iter] + ($2+$3+$4+$6); count = count + 1;
next }
    END     { print (S[2] - S[1]) * 100 / ('"$HZ"' * count * '"$sleep_len"') }
  ')
  idle_avg=`calc 100 - $cpu_avg`
  settle_count=`calc $settle_count + 1`

  echo " DONE."
  echo
  echo "Measurement:"
  echo "  + idle level: $idle_avg"
  echo
done

if test `calc $idle_avg '<' $idle_avg_min` = 1; then
  echo "system not settled. FAIL"
  exit 1
else
  echo "system settled. SUCCESS"
  exit 0
fi

