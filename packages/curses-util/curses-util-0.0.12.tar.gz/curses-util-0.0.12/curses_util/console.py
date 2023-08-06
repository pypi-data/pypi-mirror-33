#!/usr/bin/env python

import curses
import collections
import threading

console_exists = False

class SimpleConsole():
    """A singleton which sets up a console interface to handle IO in a dedicated thread and exposes a threadsafe interface.

Usage:
    def input_handler(sc, input): sc.log(input)
    sc = SimpleConsole(input_handler)
    sc.log("First Line")

where input_handler is a callable that consumes the string entered at
the main prompt. input_handler gets called in a dedicated thread, so
make sure it communicates nicely with the rest of your program.
"""

    def __init__(self, input_handler, separator_color=curses.COLOR_WHITE):
        global console_exists
        if console_exists:
            raise Exception("SimpleConsole is a singleton.")
        
        console_exists = True
        
        self._input_handler = input_handler
        self._output_buffer = []
        
        self._input_notifier = None
        self._redraw_flag = False
        self._exit_flag = False
        self._input_buffer = collections.deque()
        self._input_activity_ev = threading.Event()
        self._inputstr = ""
        self.thread = threading.Thread(target=self._io_worker)
        self.separator_color = separator_color
        self.thread.start()

    def _io_worker_input_notifier(self, scr):
        scr.timeout(50)
        while True:
            ch = scr.getch()
            if self._exit_flag: return
            if(ch == -1): continue
            
            self._input_buffer.append(ch)
            self._input_activity_ev.set()
            
    def _io_worker(self):
        scr = curses.initscr()

        curses.start_color()
        curses.init_pair(1, 0, 0)

        maxlines = None
        maxcols = None
        mainwin = None
        inputline = None
        separator = None
        inputbuffer = ""

        curses.noecho()
        curses.cbreak()
        scr.keypad(True)
        scr.clear()
        scr.refresh()

        def splitlines(lines, maxlen):
            result = []
            for line in lines:
                for subline in line.split("\n"):
                    if len(subline) > maxlen:
                        newline = ""
                        for i in range(int(len(subline) / maxlen + 1)):
                            result.append(subline[i * maxlen:(i+1) * maxlen])
                    else:
                        result.append(subline)

            return result

        def refresh_screen():
            nonlocal maxlines, maxcols, mainwin, inputline, separator, scr
            del mainwin
            del inputline
            del separator

            scr.clear()
            maxlines, maxcols = scr.getmaxyx()
            mainwin = scr.subwin(maxlines - 2, maxcols, 0, 0)
            inputline = scr.subwin(1, maxcols, maxlines - 1, 0)
            separator = scr.subwin(1, maxcols, maxlines - 2, 0)

            redraw_screen()
            
        def redraw_separator():
            separator.erase()
            curses.init_pair(1, self.separator_color, self.separator_color)
            separator.bkgd(' ', curses.color_pair(1))
            separator.refresh()

        def redraw_screen():
            redraw_mainwin()
            redraw_inputline()
            redraw_separator()

            scr.refresh()
            separator.refresh()
            mainwin.refresh()
            inputline.refresh()

        def redraw_mainwin():
            maxlines, maxcols = mainwin.getmaxyx()
            lines = splitlines(self._output_buffer, maxcols-1)
            
            if(len(lines) > maxlines):
                lines = lines[len(lines)-maxlines+1:]

            mainwin.erase()
            mainwin.addstr('\n'.join(lines))
            redraw_inputline()

        def redraw_inputline():
            nonlocal inputline
            inputline.erase()
            inputline.addstr(self._inputstr)

        def handle_input_char(ch):
            nonlocal inputbuffer
            _, maxcols = inputline.getmaxyx()
            
            if(ch >= 0x20 and ch <= 0x7E):
                inputbuffer += chr(ch)
            elif(ch == 0xA): #ENTER
                threading.Thread(target=self._input_handler,
                                 args=(self, inputbuffer)).start()
                inputbuffer = ""
            elif(ch == 21): #Ctrl-u
                inputbuffer = ""
            elif(ch == curses.KEY_BACKSPACE): #Backspace
                inputbuffer = inputbuffer[:-1]
            elif ch == curses.KEY_REFRESH or ch == curses.KEY_RESIZE or ch == 12:
                refresh_screen()

            self._inputstr=inputbuffer
            if(len(self._inputstr) >= maxcols):
                self._inputstr = self._inputstr[(len(self._inputstr) - maxcols) + 1:]
                
            redraw_inputline()
            inputline.refresh()

        # Main
        self._input_notifier = threading.Thread(target=self._io_worker_input_notifier,
                                                args=(scr,))
        self._input_notifier.start()
        refresh_screen()
        while True:
            self._input_activity_ev.wait()
            self._input_activity_ev.clear()
            
            if(self._exit_flag):
                self._input_notifier.join()
                curses.echo()
                curses.nocbreak()
                curses.endwin()
                return
            if(self._redraw_flag):
                redraw_screen()
                self._redraw_flag = False
            if self._input_buffer:
                while self._input_buffer:
                    handle_input_char(self._input_buffer.popleft())

    def refresh(self):
        """Forces a screen refresh."""
        curses.ungetch(curses.KEY_REFRESH)

    def exit(self):
        """Closes the console interface and resets the terminal, make sure this is called on exit."""
        self._exit_flag = True
        self._input_activity_ev.set()
       
    def log(self, str):
        """"Adds the provided string to the ouptut buffer"""
        self._output_buffer.append(str)
        self._redraw_flag = True
        self._input_activity_ev.set()
