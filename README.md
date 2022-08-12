# bdac
Python3 ncurses Bafang BBS02 and BBSHD configuration software, Linux based

I recently purchased a Bafang BBS02 E-Bike kit for my mountain bike. So far I've been quite
happy with everything.  One piece that I don't care for is the Windows based Pascal software
for configurng the controller.

Looking around I noticed there were a number of projects that attempt to document the RS232
protocol between the PC and the controller.  I have taken this information and written a 
Python3 Ncurses program that will run on pretty much any Linux machine from the last 10
years.  I call it Bdac.

Features:
---------
  - Runs under Linux in a console of the appropriate size.
  - Reads the Basic, Pedal Assist and Throttle Handle areas from the controller.
  - Can read a *.bdac file with all controller settings.
  - Can save a *.bdac file with all controller settings.
  - Allows you to change setting via menu interface.
  - Can write changed setting to the controller.
  - Will only write changed settings areas to save writing flash that's not changed.
  - Saves a time and date stamped *.bdac file everytime you write to the controller.
  - Saves a log (bdac.log) of all communications between the PC and controller.
  - displays human readable list of areas and settings.
  - Has help text for each setting by hitting the 'h' key.
  - Complete install and uninstall scripts.
  - badc.desktop and icon files to also run from X or Wayland desktop.
  - And of course full Python source code.
  
Installation:
-------------
  - Download the bdac-install.tar.gz file from https://www.cowlug.org/Downloads/bdac-install.tar.gz or just get the files from github
  - Untar the file and run the install.sh script as root or with sudo.
  
Uninstalling:
-------------
  - The installation will put an uninstall.sh script in /usr/local/share/bdac.
  - Run this file as root.
  
