#!/bin/sh

OS="$OSTYPE" # Get OS platform
case $OS in
    msys*) # Windows OS
        pid=$(ps aux | grep python | awk '{print $1}')
    ;;
    *) # Non Windows OS
        pid=$(ps aux | grep python | awk '{print $2}')
    ;;
esac

kill $pid