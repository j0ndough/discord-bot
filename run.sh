#!/bin/sh

OS="$OSTYPE" # Get OS platform
case $OS in
    msys*) # Windows OS
        source bot-env/Scripts/activate
    ;;
    *) # Non Windows OS
        source bot-env/bin/activate
    ;;
esac

python main.py