#!/bin/bash

# This script uninstalls the Bdac software on Linux


# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
    echo
    echo "This program must be run as user ROOT!"
    echo "You can invoke with sudo: \"sudo ./uninstall.sh\""
    echo
    exit 1
fi


    clear

    echo "BDAC"
    echo
    echo "Uninstallation script for removing Bdac... "
    echo
    echo "Please view this script before running it if you have security concerns..."
    echo
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER


    # I put sleeps in here just for human comfort:-)        
    sleep .5
    echo
    echo "Changing to /usr/local/share/bdac..."
    cd
    mwd=`pwd`
    cd /usr/local/share/bdac
    sleep .2
    echo "Removing Bdac files..."
    rm -v *
    sleep .1
    rm -v /usr/local/share/applications/bdac.desktop 
    sleep .1
    rm -v /usr/local/bin/bdac
    sleep .1
    rm -v /usr/local/bin/bdac.py
    sleep .1
    rm -v /usr/local/share/icons/bdac.png
    sleep .1
    echo "Removing /usr/local/share/bdac..."
    rm -rfv /usr/local/share/bdac

    echo "[ FINISHED... ]"


