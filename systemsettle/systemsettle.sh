#!/bin/bash

set -e

# default exit code storage
dump_error=1

calc () { awk "BEGIN{ print $* }" ;}

cleanup () {
  if ! test "$dump_error" = 0; then
    echo "System failed to settle to target idle level ($idle_avg_min)"
    echo "   + check out the following top log taken at each retry:"

    # dumb toplog indented
    while read line; do
      echo "  $line"
    done < $top_log

    echo
    # dont rerun this logic in case we get multiple signals
    dump_error=0
  fi
  rm -f $top_log $vmstat_log $vmstat_log.reduced
}

function show_usage() {
   echo "Usage:"
   echo " $0 [options]"
   echo "Options:"
   echo " -r  run forever without exiting"
   echo " -p  minimum idle percent to wait for (Default: 99)"
   echo " -c  number of times to run vmstat at each iteration (Default: 10)"
   echo " -d  seconds to delay between each vmstat iteration (Default: 6)"
   echo " -i  vmstat measurements to ignore from each loop (Default: 1)"
   echo " -m  maximum loops of vmstat before giving up if minimum idle"
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
        c)    vmstat_repeat=$OPTARG
              ;;
        d)    vmstat_wait=$OPTARG
              ;;
        i)    vmstat_ignore=$OPTARG
              ;;
        m)    settle_max=$OPTARG
              ;;
    esac
done

# minimum average idle level required to succeed
idle_avg_min=${idle_avg_min:-99}
# measurement details: vmstat $vmstat_wait $vmstat_repeat
vmstat_repeat=${vmstat_repeat:-10}
vmstat_wait=${vmstat_wait:-6}
# how many samples to ignore
vmstat_ignore=${vmstat_ignore:-1}
# how many total attempts to settle the system
settle_max=${settle_max:-10}

# set and calc more runtime values
vmstat_tail=`calc $vmstat_repeat - $vmstat_ignore`
settle_count=0
idle_avg=0

echo "System Settle run - quiesce the system"
echo "--------------------------------------"
echo
echo "  + cmd: \'vmstat $vmstat_wait $vmstat_repeat\' ignoring first $vmstat_ignore (tail: $vmstat_tail)"
echo

trap cleanup EXIT INT QUIT ILL KILL SEGV TERM
vmstat_log=`mktemp -t`
top_log=`mktemp -t`

while test `calc $idle_avg '<' $idle_avg_min` = 1 -a "$settle_prefix$settle_count" -lt "$settle_max"; do
  echo Starting settle run $settle_count:

  # get vmstat
  vmstat $vmstat_wait $vmstat_repeat | tee $vmstat_log
  cat $vmstat_log | tail -n $vmstat_tail > $vmstat_log.reduced

  # log top output for potential debugging
  echo "TOP DUMP (after settle run: $settle_count)" >> $top_log
  echo "========================" >> $top_log
  top -n 1 -b >> $top_log
  echo >> $top_log

  # calc average of idle field for this measurement
  sum=0
  count=0
  while read line; do
     idle=`echo $line | sed -e 's/\s\s*/ /g' | cut -d ' ' -f 15`
     sum=`calc $sum + $idle`
     count=`calc $count + 1`
  done < $vmstat_log.reduced

  idle_avg=`calc $sum.0 / $count.0`
  settle_count=`calc $settle_count + 1`

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
  dump_error=0
  exit 0
fi

