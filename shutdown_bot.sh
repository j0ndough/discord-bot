#!/bin/sh

# get PID on Windows
pid=$(ps aux | grep python | awk '{print $1}')
# get PID on Linux
pid=$(ps aux | grep python | awk '{print $2}')

kill $pid