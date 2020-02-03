#!/bin/bash
#
# pipeline console - An easy script to start/stop/install pipeline.
#
# By Mark Pryor
#
#path to applications, change this depending on where you saved the packages.
PTH=pipeline/
APP=( app.py monitorTemp.py timer.py )

#RPi Config file
CONFIG=/boot/config.txt

#REQUIREMENT
REQ=True

# Storage file for displaying cal and date command output
OUTPUT=/tmp/output.sh.$$

#Check to see if program is running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    echo "Please run: sudo ~/launch.sh"
    exit 1
else
    echo "Starting console..."
    trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM
fi

# Start Functions

function req_check(){
    if ! [[ $(pip freeze | grep Flask) && $(command -v python) ]] ; then
        REQ=False
    else
        REQ=True
    fi
}

function display_output(){
	local h=${1-10}			# box height default 10
	local w=${2-41} 		# box width default 41
	local t=${3-Output} 	# box title
	whiptail --backtitle "pipeline - ${t}" --title "${t}" --clear --msgbox "$(cat $OUTPUT)" ${h} ${w}
}

#Install pipeline
function install(){
    start_service
    if [ "$(cat $OUTPUT)" = "Dependancies not detected: Please Run Install Option." ]; then
        echo "Preparing to install..."
        sleep 1
        apt-get install python pip sqlite3 -y
        sleep 1
        pip install Flask
        echo "Install Complete!"
        sleep 1
    else
        echo "Install not required." >$OUTPUT
        display_output 10 30 "[===pipeline]"
    fi
}

function start_service(){
    echo "Working, Please Wait..."
    DEFAULT=--defaultno
    req_check
    if [ "$REQ" = True ]; then
        if ! ps aux | grep '/usr/bin/python' | grep app.py; then
            whiptail --yesno "Would you like to start pipeline?" $DEFAULT  10 70 2

            RET=$?
            if [ $RET -eq 1 ]; then
                echo "Service not started..." >$OUTPUT
                display_output 10 35
            else [ $RET -eq 0 ];
                for i in "${APP[@]}"; do

                    nohup python $PTH$i &
                    sleep .2
                    clear
                    echo "Starting ${i}..."
                    sleep 2
                done
                echo "pipeline service has been started! Access @ $(hostname -I)" >$OUTPUT

                display_output 16 60 "[===pipeline]"
            fi

        else
            echo "pipeline is already running! @ $(hostname -I)" >$OUTPUT
            display_output 16 60 "[===pipeline]"
        fi
    else
        echo "Dependancies not detected: Please Run Install Option." >$OUTPUT
        display_output 10 35 "[===pipeline]"
    fi
}

function stop_service(){
    DEFAULT=--defaultno
    if ! ps aux | grep '/usr/bin/python' | grep app.py; then
        echo "pipeline not running" >$OUTPUT
        display_output 10 30 "[===pipeline]"
    else
        whiptail --yesno "Would you like to stop pipeline?" $DEFAULT  10 70 2

        RET=$?
        if [ $RET -eq 1 ]; then
            echo "pipeline will continue." >$OUTPUT
            display_output 10 30 "[===pipeline]"
        else [ $RET -eq 0 ];
            killallthethings
            echo "pipeline service has been stopped!" >$OUTPUT
            display_output 10 30 "[===pipeline]"
        fi
    fi
}

function killallthethings(){
    kill $(ps aux | grep '/usr/bin/python' | grep app.py | awk '{print $2}') || echo "pipeline not running."
    sleep 1
    kill $(ps aux | grep 'python' | grep timer.py | awk '{print $2}') || echo "Timer not running."
    sleep 1
    kill $(ps aux | grep 'python' | grep monitorTemp.py | awk '{print $2}') || echo "Temperature Monitor not running."
    sleep 1
}

function goodnight() {
    whiptail --yesno "!!! Shutdown the system? !!!" $DEFAULT  10 70 2
    RET=$?
    if [ $RET -eq 1 ]; then
        echo "System Continuing..." >$OUTPUT
        display_output 10 30 "[===pipeline]"
    else [ $RET -eq 0 ];
        killallthethings
        echo "pipeline service has been stopped!" >$OUTPUT
        display_output 10 30 "[===pipeline]"
        sleep 1
        shutdown -h now
    fi
}
#echo ps aux | grep '/usr/bin/python' | awk '{print $2}
# set infinite loop
### display main menu ###
while true; do

    FUN=$(whiptail --title "[===pipeline]" --backtitle "pipeline" --menu "Setup Options" 15 50 5 --cancel-button Finish --ok-button Select \
        "1 Start" "services" \
        "2 Stop" "services"\
        "3 Install" "pipeline"\
        "4 Hault" "Shutdown System"\
        3>&1 1>&2 2>&3)

    RET=$?
    if [ $RET -eq 1 ]; then
        [ -f $OUTPUT ] && rm $OUTPUT
        exit 0
    else [ $RET -eq 0 ];

        case "$FUN" in
            1\ *) start_service ;;
            2\ *) stop_service ;;
            3\ *) install ;;
            4\ *) goodnight ;;
            *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
        esac || whiptail --msgbox "There was an error running option $FUN" 20 60 1
    fi
done
