#!/bin/sh

# activate venv for Windows
source bot-env/Scripts/activate
# activate venv for Linux
# source bot-env/bin/activate

# clear nohup.out
rm -f nohup.out
# start bot in background
nohup python main.py &