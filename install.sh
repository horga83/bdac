#!/bin/bash

# This script installs Bdac software on a Linux X11 desktop.

REMOVE()
{
    #I put sleeps in here just for human comfort:-)        
    sleep .5
    echo
    echo "Changing to /usr/local/share/bdac..."
    mwd=`pwd`
    cd /usr/local/share/bdac
    sleep .2
    echo "Removing bdac files..."
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
    cd $mwd
}

# Version 1 - May 02, 2020

# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
  echo "This program must be run as user ROOT!"
  echo "Try: \"sudo ./install.sh\""
  echo
  exit 1
fi

clear
echo "BDAC"
echo
echo "Installation script for installing Bdac... "
echo
echo "Please view this script before running it if you have security concerns..."
echo
echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER

if [ ! -e "./bdac-distribution.tar.gz" ]; then
    echo
    echo "Can't find the bdac-distribution.tar.gz file"
    echo "It should be in the same directory you ran this install.sh file from..."
    echo
    exit 1
fi

if [ -d "/usr/local/share/bdac" ]; then
    echo
    echo "Bdac is already installed, we will remove the old"
    echo "installation before installing this version"
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER
    REMOVE
    echo
    echo "Proceeding with installation..."
    sleep 2
fi


# Check distro
if ( cat /proc/version | grep -i debian >/dev/null ) ; then
  OS=Debian
elif ( cat /proc/version | grep -i arch >/dev/null ) ; then
  OS=Arch
elif ( cat /proc/version | grep -i ubuntu >/dev/null ) ; then
  OS=Debian  
fi

if [ $OS = "Debian" ]; then
    echo
    echo
    echo "It looks like you are running a Debian/Ubuntu/Mint"
    echo "distribution.  Installing requirements with apt-get..."
    echo
    sleep 2
    apt-get install python3-serial
    apt-get install python3-dev
    echo
    echo "Adding you to the \"DIALOUT\" group"
    echo
    usermod -a -G dialout $SUDO_USER
    sleep .5
elif [ $OS = "arch" ]; then
    echo
    echo
    echo "It looks like you are running an Arch based distribution."
    echo "Installing requirements with pacman..."
    echo
    sleep 2
    pacman -S python-pyserial
    echo "Adding you to the \"UUCP\" group"
    echo
    usermod -a -G uucp $SUDO_USER
    sleep .5
fi

echo
echo 
echo "Making directories under /usr/local/share..."
mkdir -pv /usr/local/share/applications
mkdir -pv /usr/local/share/bdac
mkdir -pv /usr/local/share/icons

# I put sleeps in here just for human comfort:-)        
sleep 1
echo
echo "Changing to /usr/local/share/bdac..."
mwd=`pwd`
cd /usr/local/share/bdac
sleep .5
echo "Untaring bdac files..."
tar xvzf $mwd/bdac-distribution.tar.gz
sleep .5        
echo "Copying Python and resource files..."
sleep .2
cp -v bdac.desktop /usr/local/share/applications
sleep .2
cp -v bdac /usr/local/bin
sleep .2
cp -v bdac.py /usr/local/bin
sleep .2
cp -v bdac.png /usr/local/share/icons
sleep .5
echo
echo "Making sure bdac and bdac.py are executable..."
chmod +x /usr/local/bin/bdac
chmod +x /usr/local/bin/bdac.py

echo
echo
echo "We now need to select a default terminal when running under a"
echo "Linux Graphical Desktop."
re='^[0-9]+$'
while [ 1 ]
do
    echo
    echo "Please select one of the following:"
    echo "1) GNOME/CINNAMON - gnome-terminal"
    echo "2) Mate  - mate-terminal"
    echo "3) XFCE  - xfce4-terminal"
    echo "4) Other" 
    echo -n "Your choice, or CTRL-C to exit : " ; read MYTERM
    # Is it a digit?
    if ! [[ $MYTERM =~ $re ]] ; then
        echo
        echo "Error: Not a number..."
        sleep .5
        continue
    fi
    if [ $MYTERM -lt 1 ] || [ $MYTERM -gt 4 ]; then
        echo
        echo "Must select between 1 and 4..."
        sleep .5
        continue
    else
        break
    fi
done
case "$MYTERM" in
    1)
        echo "You have selected Gnome Terminal..."
        ;;
    2)
        echo "You have selected Mate Terminal..."
        ;;
    3)
        echo "You have selected XFCE4 Terminal..."
        ;;
    4)
        echo "You have selected OTHER as your terminal..."
        echo "You will have to hand edit the /usr/local/bin/bdac file."
        ;;
esac

echo "Editing /usr/local/bin/bdac script.."    
sed -i "s/TERMINAL=[123]/TERMINAL=$MYTERM/g" /usr/local/bin/bdac
echo


echo "FINISHED..."
echo
echo "[ ***** IMPORTANT NOTES PLEASE READ ***** ]"
echo
echo "You have been added the DIALOUT group or the UUCP group depending"
echo "on whether you run Debian/Ubuntu/Mint based Linux or Arch/Manjaro"
echo "based Linux.  You may have to REBOOT for this to take effect but"
echo "you will, at the very least, have to logout and login again"
echo "If you run the \"groups\" command and DO NOT see your group, then"
echo "you will have to reboot."
echo
echo "If you are having trouble with a terminal popping up and disappearing"
echo "something is not set correctly, try running /usr/local/bin/bdac.py"
echo "and checking the error."
    
