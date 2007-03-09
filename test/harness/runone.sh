#!/bin/bash

# Set up our accessibility environment for those apps that 
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:

debugFile=`basename $1 .keys`

# Number of seconds to wait for test application to start
FAST_WAIT_TIME=10
SLOW_WAIT_TIME=20

# Run the event listener...
#
# python `dirname $0`/event_listener.py > $debugFile.events &
# sleep 2

# Run the app (or gnome-terminal if no app was given) and let it settle in.
#
if [ -n "$3" ]
then
    APP_NAME=$2
    coverageMode=$3
else
    APP_NAME=gnome-terminal
    coverageMode=$2
fi

if [ "$coverageMode" -eq "1" ]
then
    APP_WAIT_TIME=$SLOW_WAIT_TIME
else
    APP_WAIT_TIME=$FAST_WAIT_TIME
fi

if [ "$coverageMode" -eq 0 ] 	 
then
    # Run orca and let it settle in.
    orca &
    sleep 5
fi


$APP_NAME &
APP_PID=$!
sleep $APP_WAIT_TIME

# Play the keystrokes.
#
python `dirname $0`/../../src/tools/play_keystrokes.py < $1

# Terminate the running application
kill -9 $APP_PID > /dev/null 2>&1

# Terminate the running application and Orca
#
if [ "$coverageMode" -eq 0 ] 	 
then
    # Terminate Orca
    orca --quit > /dev/null 2>&1
fi

if [ "$coverageMode" -eq 0 ] 	 
then
    rm user-settings.py*
fi
