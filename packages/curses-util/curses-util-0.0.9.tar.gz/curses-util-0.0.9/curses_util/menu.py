#!/usr/bin/env python

import curses_util.util as util
import curses
import re
import signal
import sys

oitems = []
items = []
scr = util.cursesinit()
marked = set()
sh = 0
sw = 0
sel = 0
first = 0
display = None
search_query = ""
item_filter = ""

mark_color_fg = None
mark_color_bg = None
select_color_bg = None
select_color_fg = None

select_color_bg_def = curses.COLOR_CYAN
mark_color_fg_def = curses.COLOR_MAGENTA
select_color_fg_def = -1 #Default color
mark_color_bg_def = -1


def sigint(*args):
    util.cursesclean()
    sys.exit(1)

def init_colors():
    global mark_color_fg, mark_color_bg, select_color_fg, select_color_bg
        
    if not mark_color_fg or mark_color_fg > curses.COLORS:
        mark_color_fg = mark_color_fg_def
    if not mark_color_bg or mark_color_bg > curses.COLORS:
        mark_color_bg = mark_color_bg_def
    if not select_color_fg or select_color_fg > curses.COLORS:
        select_color_fg = select_color_fg_def
    if not select_color_bg or select_color_bg > curses.COLORS:
        select_color_bg = select_color_bg_def
    
    curses.init_pair(3, mark_color_fg, select_color_bg)
    curses.init_pair(1, select_color_fg, select_color_bg)
    curses.init_pair(2, mark_color_fg, mark_color_bg)
    
def draw_items():
    global items
    scr.erase()
    height, width = scr.getmaxyx()

    select_colors = curses.color_pair(1)
    mark_colors = curses.color_pair(2)
    highlight_and_select_colors = curses.color_pair(3)

    display_items = items[first:first + height]

    display_items = map(lambda x:
                        display(x).replace('\t','    ')[:width - 1],
                        display_items)
    for i,item in enumerate(display_items):
        if i == sel:
            item += (width - len(item) - 1) * " "
            if i + first in marked:
                scr.addstr(item, highlight_and_select_colors)
            else:
                scr.addstr(item, select_colors)
        elif i + first in marked:
            scr.addstr(item, mark_colors)
        else:
            scr.addstr(item)


        if i < (height - 1):
            scr.addstr("\n")

    scr.move(sel, width - 1)
    scr.refresh()

def onresize(display):
    scr.clear()
    draw_items()

def unmark_items(num):
    base = first + sel
    for i in range(num):
        marked.discard(base + i)
    move_down(num)

def mark_items(num):
    nitems = len(items)
    base = first + sel

    if base + num > nitems:
        num = nitems - base

    for i in range(num):
        marked.add(base + i)

    move_down(num)

def move_up(num):
    global sel, first

    sel -= num

    if sel < 0:
        first -= -1 * sel
        sel = 0

    if first < 0:
        first = 0
        sel = 0

def search_backward(num):
    global sel
    for _ in range(num):
        for i in range(first+sel-1, -1, -1):
            if search_query in display(items[i]):
                move_up(sel + first - i)
                break

def search_forward(num):
    global sel
    for _ in range(num):
        for i in range(first+sel+1, len(items)):
            if search_query in display(items[i]):
                move_down(i - sel - first)
                break

def move_down(num):
    global sel, first

    nitems = len(items)
    max_sel = nitems - 1 if sh > nitems else sh - 1
    max_first = 0 if sh > nitems else nitems - sh

    sel += num

    if sel > max_sel:
        if sh < nitems:
            first += sel - sh + 1
        if first > max_first:
            first = max_first
        sel = max_sel

def vend(_items, _display, markable_mode=False):
    global sh, sw, sel, first, scr, items, display, search_query
    init_colors()
    for item in items:
        if "\n" in item:
            raise Exception("Newline not permitted in menu items")


    oitems = items = _items
    sh, sw = scr.getmaxyx()
    sel = 0
    first = 0
    marked.clear()
    opnum = 0

    display = _display
    draw_items()
    while True:
        c = scr.getch()
        if chr(c) == 'g' and last_char == 'g':
            sel = 0
            first = 0
        elif chr(c) == 'G':
            if len(items) < sh:
                first = 0
                sel = len(items) - 1
            else:
                first = len(items) - sh
                sel = sh - 1
        elif c == curses.KEY_DOWN or chr(c) == 'j': #Up
            opnum = opnum if opnum else 1
            move_down(opnum)
            opnum = 0
        elif c == curses.KEY_UP or chr(c) == 'k': #Down
            opnum = opnum if opnum else 1
            move_up(opnum)
            opnum = 0
        elif c == 5: #ctrl-e
            opnum = opnum if opnum else 1

            osel = sel
            sel = sh - 1
            move_down(opnum)
            sel = osel

            opnum = 0
        elif c == 25: #ctrl-y
            opnum = opnum if opnum else 1

            osel = sel
            sel = 0
            move_up(opnum)
            sel = osel

            opnum = 0
        elif c == 6: #ctrl-f
            sel = sh - 1
            move_down(sh)
        elif c == 2: #ctrl-b
            sel = 0
            move_up(sh)
        elif chr(c) == 'f': #expensive
            item_filter = util.input("Filter: ")
            fitems = [ i
                    for i in oitems
                    if re.match(item_filter, display(i)) ]
            if len(fitems) != 0:
                items = fitems
                first = 0
                sel = 0
                marked.clear()
        elif chr(c) == 'n':
            opnum = opnum if opnum else 1
            search_forward(opnum)
            opnum = 0
        elif chr(c) == 'N':
            opnum = opnum if opnum else 1
            search_backward(opnum)
            opnum = 0
        elif chr(c) == '?':
            search_query = util.input('?')
            search_backward(1)
        elif chr(c) == '/':
            search_query = util.input('/')
            search_forward(1)
        elif chr(c) == 'q':
            util.cursesclean()
            return None
        elif chr(c) == '\n':
            util.cursesclean()
            return [ items[i] for i in marked ] if marked else [ items[first + sel] ]
        elif chr(c) == 'u':
            opnum = opnum if opnum else 1
            unmark_items(opnum)
            opnum = 0
        elif chr(c) == 'm':
            if markable_mode:
                opnum = opnum if opnum else 1
                mark_items(opnum)
            opnum = 0
        elif chr(c) == 'M':
            if sh > len(items):
                sel = int((len(items) - 1) / 2)
            else:
                sel = int((sh - 1)/2)
        elif chr(c) == 'L':
            opnum = opnum if opnum else 1
            if sh > len(items):
                sel = len(items) - 1
            else:
                sel = sh - 1

            sel -= opnum - 1
            opnum = 0
        elif chr(c) == 'H':
            opnum = opnum if opnum else 1
            sel = opnum - 1
            opnum = 0
        elif c >= ord('0') and c <= ord('9'):
            opnum *= 10
            opnum += int(chr(c))
        elif c == curses.KEY_RESIZE:
            onresize(display)

        last_char = chr(c)
        sh, sw = scr.getmaxyx()
        draw_items()
        
signal.signal(signal.SIGINT, sigint)

#Public API

class Menu():
    """A class representing a menu capable of vending items.

Usage:

    menu = Menu(mark_color_fg=curses.COLOR_MAGENTA,
                mark_color_bg=curses.COLOR_BLACK,
                select_color_bg=curses.COLOR_CYAN,
                select_color_fg=curses.COLOR_BLACK):
    
    selected = menu.vend([ 'item ' + str(i) for i in range(100) ])
"""
    def __init__(self,
                 mark_color_fg=None,
                 mark_color_bg=None,
                 select_color_bg=None,
                 select_color_fg=None):
        self.mark_color_fg = mark_color_fg
        self.mark_color_bg = mark_color_bg
        self.select_color_bg = select_color_bg
        self.select_color_fg = select_color_fg

    def _init_colors(self):
        global mark_color_fg, mark_color_bg, select_color_bg, select_color_fg
        mark_color_fg = self.mark_color_fg
        mark_color_bg = self.mark_color_bg
        select_color_bg = self.select_color_bg
        select_color_fg = self.select_color_fg

    def multi_vend(self, items, display=lambda x: x):
        """Consumes a list of items and allows the user to choose a
           subset of them. Users can mark items using the 'm' key and
           navigate using standard vi bindings (hjkl)."""
        
        global mark_color_fg, mark_color_bg, select_color_bg, select_color_fg
        try:
            self._init_colors()
            return vend(items, display, markable_mode=True)
        finally:
            util.cursesclean()

    def vend(self, items, display=lambda x: x):
        """Presents a menu which allows the user to select from a list
           of items.  If provided, the display parameter should yield
           a display string for each item in the provided list. If
           display is omitted it is the identity function and the
           provided items are expected to be strings."""
        
        try:
            self._init_colors()
            return vend(items, display)[0]
        finally:
            util.cursesclean()
