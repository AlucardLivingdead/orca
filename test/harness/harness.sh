#!/bin/bash -v
#
# harness.sh can take the following optional parameters:
#
# -c                 - analyze test coverage instead of regression testing
# -h|--help          - print a usage message
# -k <keystrokesDir> - alternate keystroke directory (default is ../keystrokes)
# -p                 - create profile information instead of regression testing
# -r <resultsDir>    - alternate results directory (default is ../results)
# -s                 - require the tester to press return between each test
#

# Determine some default paths.
#
foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes
resultsDir=$harnessDir/../results

# OpenOffice executables are installed in
# /usr/lib/openoffice/program
#
export PATH=$PATH:/usr/lib/openoffice/program

# Function to process the command line arguments.
#
coverageMode=0
profileMode=0

process_args () {
    while [ $# != 0 ]; do
        case "$1" in
            -c )
                coverageMode=1
                ;;
            -k )
                shift
                if [ $# == 0 ]; then
                    echo "Option -k requires an argument."
                    exit 1
                fi
                keystrokesDir=$1
                ;;
            -p )
                profileMode=1
                ;;
            -r )
                shift
                if [ $# == 0 ]; then
                    echo "Option -r requires an argument."
                    exit 1
                fi
                resultsDir=$1
                ;;
            -s )
                stepMode=1
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "options:"
                echo "   -c                perform code coverage analysis"
                echo "   -h, --help        print this usage message"
                echo "   -k keystrokeDir   specify an alternate keystrokes directory"
                echo "   -p                create profile information"
                echo "   -r resultsDir     specify an alternate results directory"
                echo "   -s                require a return to be pressed between keystrokes files"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
}

process_args "${@}"

# Run Orca normally or using coverage or profiling modes.
#
if [ "$coverageMode" -eq 1 ]
then
    echo generating coverage map...
    coverageDir=../coverage/`date +%Y-%m-%d_%H:%M:%S`
    orcaCommand="trace2html.py -o $coverageDir -w orca -r runorca.py"
elif [ "$profileMode" -eq 1 ]
then
    echo generating profile information...
    orcaCommand="python runprofiler.py"
else
    orcaCommand="orca"
fi

cp user-settings.py.in user-settings.py
$orcaCommand&
sleep 10

# Look in the keystrokes directory for directories.
# The name of each directory under the keystrokes directory
# is expected to be the name of an application to run.  For
# example, the gnome-terminal keystrokes should live under
# a directory called gnome-terminal.  If there isn't an
# application associated with the directory name, we just
# assume the test should apply to the desktop in general.
#
# For each application we find, we run it.  Then, we run
# the keystrokes we find in each application directory,
# taking care to tell orca to log the speech/braille output
# to specific files.
#
dirprefix=`date +%Y-%m-%d_%H:%M:%S`
testDirs=`find $keystrokesDir -type d | grep -v "[.]svn" | sort`
for testDir in $testDirs
do
    application=`basename $testDir`
    if [ $application != `basename $keystrokesDir` ]
    then

        # Check to see if the application exists.  If it does, then
        # run it.  If it doesn't, see if the name is in a list of
        # system types that we care about.  If it is, we'll only run
        # the tests under the directory if the directory name matches
        # the result of `uname`.
        #
        oldifs="$IFS"
        IFS=:
        found=0
        for dir in $PATH; do
            test -x "$dir/$application" && {
                found=1
                break
            }
        done
        IFS="$oldifs"
        outputdir=$dirprefix/$application
        currentdir=`pwd`

        COMMAND=$application
        ARGS=""

        if [ "$found" -eq 0 ]
        then
            osType=`uname`
            if [ $application == $osType ]
            then
                COMMAND=""
                found=1
            else
                echo Skipping $application because I cannot find it
                continue
            fi
        else
            # Don't let gnome-terminal change the title on us -- it
            # wreaks havoc on the output.
            #
            if [ "$application" == "gnome-terminal" ]
            then
                gconftool-2 --set /apps/gnome-terminal/profiles/Default/title_mode --type string ignore
            fi

            # Tell OpenOffice Writer and Calc to not attempt to
            # recover edited files after a crash.
            #
            if [ "$application" == "swriter" ] || [ "$application" == "scalc" ] || [ "$application" == "soffice" ] || [ "$application" == "soffice" ]
            then
                SOFFICE=1
                ARGS="-norestore"
            fi
	
	    # If we're using Firefox, give it a known profile to work from.
	    #
	    if [ "$APP_NAME" = "firefox" ]
	    then
		foo=`dirname $0`
		harnessDir=`cd $foo; pwd`
		ARGS="-profile $harnessDir/../html/FirefoxProfile"
	    fi
        fi

        hasTests=`find $testDir -type f -name "*.py" | sort`
        if [ "x$hasTests" == "x" ]
        then
            echo Skipping $application because there are no tests for it
            continue
        fi

        echo ========================================
        echo Running tests for $application

        # We run under ./tmp as a means to help provide consistent
        # output for things that expose directory paths.
        #
        mkdir -p ./tmp/$application
        cd ./tmp/$application

        PID=0
        testFiles=`find $testDir -type f -name "*.py" | sort`
        for testFile in $testFiles
        do
            # Make sure the application is running, restarting it if
            # necessary.
            #
            if [ "x$COMMAND" != "x" ]
            then
                # Allow us to pass parameters to the command line of
                # the application.
                #
                # If a <testfilename>.params file exists, it contains
                # parameters to pass to the command line of the
                # application.
                #
                # NOTE: the type of application we expect to be able
                # to use applications with are applications like
                # gedit, soffice, nautilus, etc., which don't launch
                # a new application instance each time you run them
                # from the command line.
                #
                PARAMS_FILE=$testDir/`basename $testFile .py`.params
                if [ -f $PARAMS_FILE ]
                then
                    PARAMS=`cat $PARAMS_FILE`
                fi

                PID_RUNNING=`ps -p $PID > /dev/null 2>&1`
                if [ $? -eq 1 ]
                then
                    if [ $PID -ne 0 ]
                    then
                        echo "ERROR: $COMMAND $ARGS CRASHED!  RESTARTING..."
                    fi

                    echo "COMMAND: $COMMAND $ARGS $PARAMS"

                    $COMMAND $ARGS $PARAMS &
                    if [ "x$SOFFICE" == "x1" ]
                    then
                        PID=$(ps -eo pid,ruid,args | grep soffice | grep -v grep | awk '{ print $1 }')
                    else
                        PID=$!
                    fi
                    sleep 10
                elif [ "x$PARAMS" != "x" ]
                then
                    echo "COMMAND: $COMMAND $ARGS $PARAMS"
                    $COMMAND $ARGS $PARAMS &
                fi
            fi

            echo === $testFile
            newResultsFile=`basename $testFile .py`
            wget --output-file /dev/null --post-data="debug:0:./tmp/$application/$newResultsFile" localhost:20433
            wget --output-file /dev/null --post-data="log:./tmp/$application/$newResultsFile" localhost:20433
            python $testFile
            wget --output-file /dev/null --post-data="log:" localhost:20433
            wget --output-file /dev/null --post-data="debug:10000" localhost:20433

            # Copy the results (.orca) file to the output directory.
            # This is the file that will be used for regression
            # testing.
            mkdir -p $currentdir/$outputdir

            # Filter the results...
            #
            # For braille, get rid of spurious "Desktop Frame" lines which
            # happen when there's enough of a pause for nautilus to think
            # it has focus.
            #
            # For speech, we do the same thing, but we need to get rid of
            # several lines in a row.  So, we use sed.
            #
            grep -v "Desktop Frame" $newResultsFile.braille > $currentdir/$outputdir/$newResultsFile.braille
            mv $newResultsFile.braille $currentdir/$outputdir/$newResultsFile.braille.unfiltered
            sed "/speech.speakUtterances utterance='Desktop frame'/,/speech.speakUtterances utterance='Icon View layered pane'/ d" $newResultsFile.speech > $currentdir/$outputdir/$newResultsFile.speech
            mv $newResultsFile.speech $currentdir/$outputdir/$newResultsFile.speech.unfiltered
            mv $newResultsFile.debug $currentdir/$outputdir
            rm -f *

            if [ "x$stepMode" == "x1" ]
                then
                echo Press Return to continue...
                read foo
            fi
        done
        if [ "x$application" == "xfirefox" ]
	then
	    pkill firefox
	else
            kill -9 $PID > /dev/null 2>&1
	fi
        cd $currentdir
        rm -rf ./tmp/$application
    fi
done

python quit.py
rm user-settings.py
rm -f user-settings.pyc

if [ "$coverageMode" -eq 1 ]
then
    echo ...finished generating coverage map
fi

if [ "$profileMode" -eq 1 ]
then
    mkdir -p ../profile
    profileFilePrefix=../profile/`date +%Y-%m-%d_%H:%M:%S`
    python -c "import pstats; pstats.Stats('orcaprof').sort_stats('cumulative').print_stats()" > $profileFilePrefix.txt
    mv orcaprof $profileFilePrefix.orcaprof
    echo ...finished generating profile information:
    echo "   $profileFilePrefix.txt"
fi

echo $dirprefix completed at `date +%Y-%m-%d_%H:%M:%S`
