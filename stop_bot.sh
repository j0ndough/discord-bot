#!/bin/sh

OS="$OSTYPE" # Get OS platform
case $OS in
    msys*) # Windows OS
        pid=$(ps aux | grep python | awk '{print $1}' | head -n 1)
    ;;
    *) # Non Windows OS
        pid=$(ps aux | grep python | awk '{print $2}' | head -n 1)
    ;;
esac

kill $pid