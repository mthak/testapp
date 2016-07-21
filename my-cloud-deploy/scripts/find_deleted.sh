#!/bin/bash
set -e
# find list of open file which are open but deleted and truncate those files
data=$(lsof -a +L1 | tail -n +2 | awk '{print $2}')
for pids in $data
do 
  files=$(ls -l /proc/$pids/fd | grep -i deleted | awk '{print $9}')
  for fds in $files
  do
    `>/proc/$pids/fd/$fds`
  done
done
