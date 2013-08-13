#!/bin/bash

calc () { awk "BEGIN{ print $* }" ;}

if test -z "$1"; then
   echo "ERROR: you need to provide the average idle value"
   echo "Usage: systemsettle.sh <avg-idle>"
   echo "       - e.g. systemsettle.sh 99.25"
   exit 129
fi

# minimum average idle level required to succeed
quiesce_min=$1

# how many total attempts to settle the system
settle_max=10

# measurement details: vmstat $vmstat_wait $vmstat_repeat
vmstat_wait=6
vmstat_repeat=10

# how many samples to ignore
vmstat_ignore=1

# tweak cut field by arch
if uname -m | grep -q armv7; then
  idle_pos=16
elif uname -m | grep -q i.86; then
  idle_pos=15
else
  echo "machine \'`uname -m`\' not supported"
  exit 128
fi

# set and calc more runtime values
vmstat_tail=`calc $vmstat_repeat - $vmstat_ignore`
settle_count=0
quiesce_level=0

echo "System Settle run - quiesce the system"
echo "--------------------------------------"
echo
echo "  + cmd: \'vmstat $vmstat_wait $vmstat_repeat\' ignoring first $vmstat_ignore (tail: $vmstat_tail)"
echo

vmstat_log=`mktemp -t`
top_log=`mktemp -t`

while test `calc $quiesce_level '<' $quiesce_min` = 1 -a "$settle_count" -lt "$settle_max"; do
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

  quiesce_level=`calc $sum.0 / $count.0`
  settle_count=`calc $settle_count + 1`

  echo
  echo "Measurement:"
  echo "  + idle level: $quiesce_level"
  echo "  + idle sum: $sum / count: $count"
  echo
done

if test `calc $quiesce_level '<' $quiesce_min` = 1; then
  echo "System failed to settle to target idle level ($quiesce_min)"
  echo "   + check out the following top log taken at each retry:"
  cat $top_log
  echo
  echo "system did not settle. FAILED."
  exit 1
else
  echo "system settled. SUCCESS"
  exit 0
fi

