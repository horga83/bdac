# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Footer

# Todo
# - Add info to report


import os
import sys
import json
import time
import curses
import datetime

sys.path.append('/usr/local/share/bdac')

from time import sleep
from serial import Serial, SerialException
from collections import OrderedDict
from binascii import hexlify
from bdac_help import help_dict

CURSOR_INVISIBLE = 0    # no cursor
CURSOR_NORMAL = 1       # Underline cursor
CURSOR_BLOCK = 2        # Block cursor

NOCHAR = -1

class BdacTerm():

    def __init__(self, get_basic_config, 
                       get_pas_config,
                       get_throttle_config,
                       read_config,
                       basic_dict,
                       pas_dict,
                       throttle_dict,
                       test_data,
                       PORT,
                       VERSION,
                       VERSION_DATE):

        self.screen = None
        self.port = PORT
        self.version = VERSION
        self.version_date = VERSION_DATE
        self.test_data = test_data
        self.basic_dict = basic_dict
        self.pas_dict = pas_dict
        self.throttle_dict = throttle_dict
        self.get_basic_config = get_basic_config
        self.get_pas_config = get_pas_config
        self.get_throttle_config = get_throttle_config
        self.read_config = read_config

    def setup_screen(self):
        self.cur = curses.initscr()  # Initialize curses.
        curses.start_color()

        if curses.termname() == b'linux':
            self.X0 = 0
            self.Y0 = 0
        else:
            self.X0 = 1
            self.Y0 = 1
            self.cur.box()
            self.cur.refresh()
            y, x = self.cur.getmaxyx()
            if y < 28 or x < 90:
                curses.endwin()
                print("\nYour screen is to small to run bdac, it must be")
                print("at least 28 lines by 90 columns...\n")
                print("Consider changing your terminal profile so you do not have")
                print("to resize the window all the time...\n")
                print("If you are using PUTTY, make sure you go to")
                print("Connection->Data and set your terminal type to \"linux\" as well\n\n\n")
                sys.exit(1)

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)


        curses.cbreak()
        curses.raw()
        #curses.noecho()
        curses.nonl()
        self.cur.refresh()
        self.screen = curses.newwin(28,88,self.X0, self.Y0)
        self.screen.refresh()
        self.screen.nodelay(1)
        self.screen.keypad(1)
        self.screen.scrollok(True)
        self.screen.idlok(1)
        self.screen.setscrreg(0,19)
        return self.screen


    def reset(self):
        self.visibleCursor = True
        self.screen.erase()
        #self.cursor_home()
        curses.curs_set(CURSOR_NORMAL)


    def terminate(self):
        curses.endwin() # End screen (ready to draw new one, but instead we exit)

    def show_intro(self):
        helptext = """
            Welcome to:
             _         _            
            | |__   __| | __ _  ___ 
            | '_ \ / _` |/ _` |/ __|
            | |_) | (_| | (_| | (__ 
            |_.__/ \__,_|\__,_|\___|  """
        # created with figlet

        self.screen.erase()
        self.screen.addstr(2, 2, helptext)
        self.screen.addstr(12,20, self.version)
        self.screen.addstr(13,20, self.version_date)
        self.screen.addstr(14,20,"By George Farris - VE7FRG")
        self.screen.addstr(17,13, "Bafang BBS02 Controller Configuration System...")
        self.screen.addstr(18,13, "Using serial port [ {0} ]".format(self.port))
        if self.test_data:
            self.screen.addstr(20,13, "Attention:",curses.color_pair(0)|curses.A_BLINK)
            self .screen.addstr(20,24, "Using test data, writing to controller disabled!")
        self.screen.refresh()


    def popup_config_select(self, config_changed): 
        cl = ['Edit Basic Configuration', 
              'Edit Pedal Assist Configuration', 
              'Edit Throttle Configuration', 
              'Write Controller Flash',
              'Read File', 
              'Save File',
              'View Report', 
              'Quit']

        popup = curses.newwin(14, 50, 8, 20)
        popup.attrset(curses.color_pair(0))
        for i in range(len(cl)):
            popup.addstr(i + 3, 9, cl[i], curses.color_pair(0))
            popup.addstr(12, 11, "<Enter> to select, 'q' quits", curses.color_pair(0) | curses.A_BOLD)
        #popup.border('|', '|', '-', '-', '+', '+', '+', '+')
        popup.box()
        popup.addstr(0, 16, '[Select Function]', curses.color_pair(0) | curses.A_BOLD)
        popup.nodelay(0)
        popup.keypad(1)
        curses.curs_set(0)
        popup.refresh()

        if config_changed:
            self.screen.addstr(27,2,'Alert:', curses.color_pair(0) | curses.A_BLINK)
            self.screen.addstr(27,9,'Your Configuration has changed, consider saving or writing to flash...')
            self.screen.refresh()

        # get the index to place the cursor
        idx = 0
        popup.addstr(idx + 3, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)

        while True:
            c = popup.getch()
            if c == curses.KEY_DOWN:
                if idx + 1 < len(cl):
                    popup.addstr(idx + 3, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx + 3, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
            elif c == curses.KEY_UP:
                if idx - 1 >= 0:
                    popup.addstr(idx + 3, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx + 3, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
                popup.refresh()

            elif curses.keyname(c) == b'^M':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return(cl[idx])

            elif chr(c) == 'q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return (None)

    # Select configuration areas BASIC. PEDAL ASSIST and THROTTLE
    def show_control(self):
        config_changed = False
        flash_read = False

        while True:
            file_operation = False  # don't continue into up down select if file op
            dic = OrderedDict()
            curses.curs_set(CURSOR_INVISIBLE)

            # read controller flash only once
            if not flash_read:
                self.screen.erase()
                self.screen.addstr(12,10, "Reading the controller flash areas.....", curses.A_BLINK)
                self.screen.refresh()
                self.get_basic_config()
                self.screen.addstr(13,14, "Reading BASIC flash area.....")
                self.screen.refresh()
                self.get_pas_config()
                self.screen.addstr(14,14, "Reading PEDAL ASSIST flash area.....")
                self.screen.refresh()
                self.get_throttle_config()
                self.screen.addstr(15,14, "Reading THROTTLE HANDLE flash area.....")
                self.screen.refresh()
                sleep(1.5)
                flash_read = True

            self.screen.erase()
            self.screen.refresh()

            # Pop up the function selection screen and get selection
            resp = self.popup_config_select(config_changed)

            if resp == None:
                sys.exit(0)
            if resp == 'Edit Basic Configuration':
                dic = self.basic_dict
            elif resp == 'Edit Pedal Assist Configuration':
                dic = self.pas_dict
            elif resp == 'Edit Throttle Configuration':
                dic = self.throttle_dict
            elif resp == 'View Report':
                file_operation = True
                self.show_report()
            elif resp == 'Read File':
                err = False
                file_operation = True
                fname = self.popup_filename()
                if fname != None:
                    try:
                        f = open(fname, 'r')
                    except:
                        self.screen.erase()
                        self.screen.refresh()
                        self.popup_error('Could not open\n{0}\nfor reading'.format(fname))
                        err = True           
                    if not err:
                        # build one dictionary to hold the other 3
                        fd = OrderedDict()
                        # read it from the json file
                        fd = json.load(f)
                        # add them
                        self.basic_dict =  fd['basic']
                        self.pas_dict = fd['pas']
                        self.throttle_dict = fd['throttle']
                        err = False
                        config_changed = True
                        f.close()
                 
            elif resp == 'Save File':
                err = False
                file_operation = True
                fname = self.popup_filename()
                if fname != None:
                    try:
                        f = open(fname, 'w')
                    except:
                        self.screen.erase()
                        self.screen.refresh()
                        self.popup_error('Could not open\n{0}\nfor writing'.format(fname))
                        err = True
                    if not err:              
                        # build one dictionary to hold the other 3
                        fd = OrderedDict()
                        # add them
                        fd['basic'] = self.basic_dict
                        fd['pas'] = self.pas_dict
                        fd['throttle'] = self.throttle_dict
                        #write them to a json file
                        json.dump(fd, f)
                        f.close()
                        err = False
                        config_changed = False
                        self.screen.erase()
                        self.screen.refresh()

            elif resp == 'Write Controller Flash':
                if self.test_data:
                    self.popup_error("Using test data, writing disabled!")
                    continue
                file_operation = True

                # temp dictionaries to compare to controller              
                b = self.basic_dict.copy()
                p = self.pas_dict.copy()
                t = self.throttle_dict.copy()

                self.screen.erase()
                self.screen.addstr(12,10, "Reading the controller flash areas.....", curses.A_BLINK)
                self.screen.refresh()
                sleep(1) # at least show briefly if read is quick
                
                # get actual controller data
                self.basic_dict = self.get_basic_config()
                self.pas_dict = self.get_pas_config()
                self.throttle_dict = self.get_throttle_config()
                flash_read = True

                self.screen.erase()
                self.screen.refresh()

                # compare data to see if it has changed, only write changed areas
                if b != self.basic_dict:
                    self.screen.addstr(12,10, "Writing BASIC controller flash area.....")
                    self.screen.refresh()
                    sleep(1) # at least show briefly if read is quick
                    frame = bytearray()
                    frame.append(0x16)  # write command
                    frame.append(0x52)  # section
                    frame.append(0x18)  # packet length
                    c = 0x52 + 0x18
                    for key in b:
                        frame.append(b[key][0])
                        c = c + b[key][0]
                    checksum = c % 256
                    frame.append(checksum)
                    resp = self.read_config(frame)
                    if resp[1] != 0x18:
                        self.screen.addstr(13,10,"Received error code {0} when writing to BASIC config".format(resp[2]))
                    else:
                        self.screen.addstr(13,10,"Successfully written to BASIC controller flash...")
                    self.screen.refresh()
                
                if p != self.pas_dict:
                    self.screen.addstr(15,10, "Writing PEDAL ASSIST controller flash area.....")
                    self.screen.refresh()
                    sleep(1) # at least show briefly if read is quick
                    frame = bytearray()
                    frame.append(0x16)  # write command
                    frame.append(0x53)  # section
                    frame.append(0x0b)  # packet length (11)
                    c = 0x53 + 0x0b
                    for key in p:
                        frame.append(p[key][0])
                        c = c + p[key][0]
                    checksum = c % 256
                    frame.append(checksum)
                    resp = self.read_config(frame)
                    if resp[1] != 0x0b:
                        self.screen.addstr(16,10,"Received error code {0} when writing to PAS config".format(resp[2]))
                    else:
                        self.screen.addstr(16,10,"Successfully written to PAS controller flash...")
                    self.screen.refresh()
                
                if t != self.throttle_dict:
                    self.screen.addstr(18,10, "Writing THROTTLE controller flash area.....")
                    self.screen.refresh()
                    sleep(1) # at least show briefly if read is quick
                    frame = bytearray()
                    frame.append(0x16)  # write command
                    frame.append(0x54)  # section
                    frame.append(0x06)  # packet length
                    c = 0x54 + 0x06
                    for key in t:
                        frame.append(t[key][0])
                        c = c + t[key][0]
                    checksum = c % 256
                    frame.append(checksum)
                    resp = self.read_config(frame)
                    if resp[1] != 0x06:
                        self.screen.addstr(19,10,"Received error code {0} when writing to THROTTLE config".format(resp[2]))
                    else:
                        self.screen.addstr(19,10,"Successfully written to THROTTLE controller flash...")
                    self.screen.refresh()
                sleep(3)
                
                # write a time stamped file
                try:
                    tl = time.localtime()
                    timestamp = time.strftime('%b-%d-%Y-%H:%M:%S', tl)
                    filename = (timestamp + '-config.bdac')

                    f = open(filename, 'w')
                    # build one dictionary to hold the other 3
                    fd = OrderedDict()
                    # add them
                    fd['basic'] = b
                    fd['pas'] = p
                    fd['throttle'] = t
                    #write them to a json file
                    json.dump(fd, f)
                    f.close()
                except:
                    pass
                config_changed = False

            elif resp == 'Quit':
                sys.exit(0)
            self.screen.erase()
            self.screen.refresh()

            title = "{0} Bdac Configuration".format(resp)
            x = int((79 - len(title)) / 2)
            self.screen.addstr(0,x,title, curses.A_BOLD)

            # Add dictionary to screen and build index for navigation
            index = []
            items = []
            # remember all curses stuff is (y,x) for location, not (x,y)
            y = 2
            for key in dic:
                self.screen.addstr(y,2, "{0}\t{1}\t{2}".format(key, dic[key][0],dic[key][1]))
                items.append([key, dic[key][0],dic[key][1]])
                index.append(items[y-2])
                y += 1

            self.screen.addstr(27, 20, "Press <Enter> to select, 'h' for help, 'q' to go back",
                                    curses.color_pair(0)|curses.A_BOLD)
            self.screen.refresh()

            if not file_operation:
                # now process UP / DOWN arrows keys
                config_changed = self.up_down_select(dic, index, config_changed)

            # If conf changed save in original dictionary unless it's a file operation
            # If we read in a file we don't want to write over the dictionaries.
            if config_changed and file_operation == False:
                if resp == 'Edit Basic Configuration':
                    self.basic_dict = dic
                elif resp == 'Edit Pedal Assist Configuration':
                    self.pas_dict = dic
                elif resp == 'Edit Throttle Configuration':
                    self.throttle_dict = dic


    def up_down_select(self, dic, index, config_changed):
        self.screen.nodelay(0)
        self.screen.keypad(1)
        curses.curs_set(0)

        x = 2
        val_x = 8   # position of value field
        idx = 0
        offset = 2

        s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
        self.screen.move(idx+offset, x)
        self.screen.clrtoeol()
        self.screen.addstr(idx+offset, x, s ,curses.color_pair(0)|curses.A_REVERSE|curses.A_STANDOUT)
        curses.curs_set(CURSOR_INVISIBLE)
        self.screen.refresh()

        while True:
            curses.flushinp()
            c = self.screen.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(index):
                    s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
                    self.screen.clrtoeol()
                    self.screen.addstr(idx+offset, x, s ,curses.color_pair(0))
                    idx += 1
                    self.screen.clrtoeol()
                    s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
                    self.screen.addstr(idx+offset, x, s ,curses.color_pair(0)|curses.A_REVERSE|curses.A_STANDOUT)
                    self.screen.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 0:
                    s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
                    self.screen.clrtoeol()
                    self.screen.addstr(idx+offset, x, s ,curses.color_pair(0))
                    idx -= 1
                    s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
                    self.screen.clrtoeol()
                    self.screen.addstr(idx+offset, x, s ,curses.color_pair(0)|curses.A_REVERSE|curses.A_STANDOUT)
                    self.screen.refresh()

            elif curses.keyname(c) == b'^M':
                key, val, des = s.split('\t')
                
                self.screen.move(idx+offset,val_x)
                curses.curs_set(CURSOR_BLOCK)
                curses.echo()
                self.screen.refresh()
                
                # if <enter> is hit  without value don't go boom
                i = -1
                try:
                    i = int(self.screen.getstr(3))
                except:
                    pass
                if i >= 0 and i <= 255:
                    dic[key][0] = i
                    index[idx][0] = key
                    index[idx][1] = i
                    index[idx][2] = des
                s = "{0}\t{1}\t{2}".format(index[idx][0], index[idx][1], index[idx][2])
                self.screen.move(idx+offset,x)
                self.screen.clrtoeol()
                self.screen.addstr(idx+offset, x, s ,curses.color_pair(0)|curses.A_REVERSE|curses.A_STANDOUT)
                #print(dic, file = sys.stderr)
                self.screen.touchwin()
                self.screen.refresh()
                config_changed = True

            elif chr(c) == 'h' or chr(c) == 'H':
                key, val, des = s.split('\t')
                if 'ALC' in key:
                    key = 'ALC0-9'
                if 'ALS' in key:
                    key = 'ALC0-9'
                # These guys have indextical keys in PAS and THROTTLE
                if key == 'DA' and dic == self.pas_dict:
                    key = 'DA-PAS'
                if key == 'SL' and dic == self.pas_dict:
                    key = 'SL-PAS'
                if key == 'SC' and dic == self.pas_dict:
                    key = 'SC-PAS'
                if key == 'DA' and dic == self.throttle_dict:
                    key = 'DA-THR'
                if key == 'SL' and dic == self.throttle_dict:
                    key = 'SL-THR'
                if key == 'SC' and dic == self.throttle_dict:
                    key = 'SC-THR'
                self.popup_help(help_dict[key])
            elif chr(c) == 'q' or chr(c) == 'Q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return(config_changed)

    def popup_help(self, text):
        try:
            popup = curses.newwin(19, 82, 3, 6)
            popup.addstr(1, 1, text)
            #popup.border('|','|','-','-','+','+','+','+')
            popup.box()
            popup.addstr(0,18, "[ Bafang BBS02 Controller Help ]",curses.color_pair(0)|curses.A_BOLD)
            popup.addstr(17,25, "Press any key to close help",curses.color_pair(0)|curses.A_BOLD)
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        c = popup.getch()
        curses.curs_set(CURSOR_NORMAL)
        self.screen.touchwin()
        self.screen.refresh()

    def popup_filename(self):
        try:
            popup = curses.newwin(6, 78, 10, 5)
            popup.attrset(curses.color_pair(0))
            popup.box()
            #popup.border('|', '|', '-', '-', '+', '+', '+', '+')
            popup.addstr(0, 2, "[ ")
            popup.addstr(os.getcwd())
            popup.addstr(" ]")
            popup.addstr(2, 2, "File: ")
            popup.addstr(4,2, "Type filename and press <Enter> or just press <Enter> to exit")
            popup.move(2,8)
            curses.echo()
            s = popup.getstr().decode(encoding="utf-8")
            sfile = os.path.join(os.getcwd(), s)
            popup.refresh()
            if s == "":
                return None
            else:
                return sfile
        except:
            pass

    def popup_error(self, text):
        try:
            popup = curses.newwin(8, 49, 10, 20)
            popup.attrset(curses.color_pair(0))
            #popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(2, 1, text)
            popup.addstr(6, 8, "Hit <ENTER> to return...")

            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        c = popup.getch()
        curses.curs_set(CURSOR_NORMAL)
        self.screen.touchwin()
        self.screen.refresh()

    def show_report(self):
        wy,wx=self.screen.getmaxyx()

        data = "Current Bafang controller flash settings with explainations.\n\n"
        data += '[Basic]\n'
        for key in self.basic_dict:
            data += "{0}\t{1}\t{2}\n".format(key, self.basic_dict[key][0],self.basic_dict[key][1])
    
        data += '\n[Pedal Assist]\n'
        for key in self.pas_dict:
            data += ("{0}\t{1}\t{2}\n".format(key, self.pas_dict[key][0],self.pas_dict[key][1]))
    
        data += '\n[Throttle Handle]\n'
        for key in self.throttle_dict:
            data += "{0}\t{1}\t{2}\n".format(key, self.throttle_dict[key][0],self.throttle_dict[key][1])

        if type(data) == str:
            data = data.split('\n')

        pady = max(len(data)+3,wy)
        padx = wx

        max_x = wx
        max_y = pady-wy

        pad = curses.newpad(pady,padx)

        #pad.addstr(0,0,"[HOME / END / UP / DOWN / \"q\" to quit and \"s\" to save]",curses.color_pair(0)|curses.A_BOLD)
        pad.addstr(0,0,"[ HOME / END / UP / DOWN / \"q\" to quit ]",curses.color_pair(0)|curses.A_BOLD)
        for i,line in enumerate(data):
            if str(line) == '[Basic]' or str(line) == '[Pedal Assist]' or str(line) == '[Throttle Handle]':
                pad.addstr(i+2,0,str(line),curses.color_pair(0)|curses.A_BOLD)
            else:
                pad.addstr(i+2,0,str(line))
        x=0
        y=0

        inkey=0
        self.screen.nodelay(0)
        while inkey != 'q':
            pad.refresh(y,x,self.X0,self.Y0,wy-1,wx)
            inkey = self.screen.getkey()

            if inkey=='KEY_UP':y=max(y-1,0)
            elif inkey=='KEY_DOWN':y=min(y+1,max_y)
            elif inkey=='KEY_HOME':y=0
            elif inkey=='KEY_END':y=max_y

        curses.flushinp()
        pad.clear()
        self.screen.nodelay(1)
        self.screen.touchwin()
        self.screen.refresh()

    def process_key(self, c):
        if curses.keyname(c) == b'^A':  # Command Key
            self.parse_ctrl_a()
        elif chr(c) == 'q' or chr(c) == 'Q':
            sys.exit()
        elif curses.keyname(c) == b'^M':
            self.show_control()

    def parse_ctrl_a(self):
        c = NOCHAR
        while c == NOCHAR:
            c = self.screen.getch()
        s = chr(c)
        while True:
            if s == 'x' or s == 'X':    # Exit
                sys.exit(0)
            elif s == 'z' or s == 'Z':
                s = self.popup_help()
            else:
                break  # get out on ^M or any non command key

#=======================================================================
# GUI Main
#=======================================================================
    def gui_main(self, scr, term):
        scn = term.setup_screen()
        term.reset()
        
        # if curses.termname() == 'linux':
        self.BACKSPACE = curses.KEY_BACKSPACE
        #else:
        #    self.BACKSPACE = 127  # xterms do this
        
        first_char = True
        date_string = ''
        today = datetime.datetime.today()

        # Loop time makes sure process doesn't run wild
        loop_time = 0.0

        self.show_intro()
        curses.curs_set(CURSOR_INVISIBLE)
        
        while True:
            c = NOCHAR

            c = scn.getch()
            if c != NOCHAR:
                loop_time = 0.0

                if first_char:
                    term.screen.erase()
                    first_char = False
                    if chr(c) == 'q' or chr(c) == 'Q':
                        sys.exit()
                    if curses.keyname(c) != b'^A':  # Command Key
                        self.show_control()
                else:
                    self.process_key(c)
                

            if loop_time <= 0.1:
                loop_time += 0.000001
            else:
                time.sleep(loop_time)
