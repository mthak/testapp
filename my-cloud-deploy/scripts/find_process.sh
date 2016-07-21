#!/bin/bash
# Find if a porcess is already using the port required by this application 
# iF yes then kill that process 
port=$1
lsof -i :$port | tail -n +2 | awk '{print $2}'| xargs kill -9
