#!/bin/bash

# set -x

# Set up our accessibility environment for those apps that 
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:

debugFile=`basename $1 .keys`

# Set up our local user settings file for the output format we want.
#
# If a <testfilename>.settings file exists, should use that instead of 
# the default user-settings.py.in.
# We still need to run sed on it, to adjust the debug filename and 
# create a user-settings.py file in the tmp directory.
#
# (Orca will look in our local directory first for user-settings.py
# before looking in ~/.orca)
#
SETTINGS_FILE=`dirname $1`/$debugFile.settings
if [ ! -f $SETTINGS_FILE ]
then
    SETTINGS_FILE=`dirname $0`/user-settings.py.in
fi
echo "Using settings file:" $SETTINGS_FILE
sed "s^%debug%^$debugFile.orca^g" $SETTINGS_FILE > user-settings.py

if [ -n "$3" ]
then
    APP_NAME=$2
    getCodeCoverage=$3
else
    APP_NAME=gnome-terminal
    getCodeCoverage=$2
fi
echo "getCodeCoverage=" $getCodeCoverage

# Run the event listener...
#
# python `dirname $0`/event_listener.py > $debugFile.events &
# sleep 2

# Run orca and let it settle in, unless we are getting code coverage
#
if [ "$getCodeCoverage" -eq 0 ]
then
    orca &
    sleep 5
fi

# Run the app (or gnome-terminal if no app was given) and let it settle in.
#
$APP_NAME &
APP_PID=$!
sleep 5

# Play the keystrokes.
#
python `dirname $0`/../../src/tools/play_keystrokes.py < $1

# Terminate the running application and Orca
#

if [ "$getCodeCoverage" -eq 0 ]
then
    orca --quit > /dev/null 2>&1
fi

kill -9 $APP_PID > /dev/null 2>&1

rm user-settings.py*
