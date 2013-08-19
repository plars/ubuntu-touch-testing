#!/bin/bash

set -e

# default exit code storage
dump_error=1

calc () { awk "BEGIN{ print $* }" ;}

cleanup () {
  if ! test "$dump_error" = 0; then
    echo "Check out the following top log taken at each retry:"

    echo
    # dumb toplog indented
    while read line; do
      echo "  $line"
    done < $top_log
    # dont rerun this logic in case we get multiple signals
    dump_error=0
  fi
  rm -f $top_log $top_log.reduced
}

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
   echo "     percent is not reached (Default: 1)"
   exit 129
}

while getopts "h?rp:c:d:i:m:" opt; do
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
echo

trap cleanup EXIT INT QUIT ILL KILL SEGV TERM
top_log=`mktemp -t`

while test `calc $idle_avg '<' $idle_avg_min` = 1 -a "$settle_prefix$settle_count" -lt "$settle_max"; do
  echo -n "Starting system idle measurement (run: $settle_count) ... "

  # get top
  echo "TOP DUMP (after settle run: $settle_count)" >> $top_log
  echo "========================" >> $top_log
  top -b -d $top_wait -n $top_repeat >> $top_log
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

