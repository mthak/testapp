#!/bin/bash
set -e
port=$1
# delete the drop policy in iptables for the port number we are using 
val=$(iptables -L --line-numbers | grep -i drop | grep -i $port | awk '{print $1}')
if [ -n "$val" ]; then
   iptables -D INPUT $val
fi
# Add accept policy in iptables for port numbers we are adding
iptables -A INPUT -p tcp --dport $port -j ACCEPT
iptables-save
echo $?
