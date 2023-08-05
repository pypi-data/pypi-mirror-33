import curses

scr = None

def cursesinit():
    global scr
    scr = curses.initscr()

    curses.start_color()
    curses.use_default_colors()
    
    try:
        curses.curs_set(0)
    except:
        pass

    curses.noecho()
    curses.cbreak()
    scr.keypad(True)
    scr.clear()
    scr.refresh()
    return scr

def cursesclean():
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def input(prompt):
    height, maxw = scr.getmaxyx()
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    inv = curses.color_pair(8)

    cursor = 0
    buf = ""
    start = 0
    xoff = len(prompt)
    maxw -= xoff + 1

    def draw():
        nonlocal cursor, buf, start, xoff, maxw

        upper = start + maxw
        if upper > len(buf):
            upper = len(buf)

        if cursor >= len(buf):
            upper = len(buf)
            cursor = upper
            start = upper - maxw + 1
            if start < 0:
                start = 0

        scr.move(height - 1, 0)
        scr.clrtoeol()
        scr.move(height - 1, 0)
        scr.addstr(prompt)
        for i,c in enumerate(buf[start:upper]):
            if i+start == cursor:
                scr.addstr(str(c), inv)
            else:
                scr.addch(c)

        if cursor >= upper:
            scr.addstr(' ', inv)

        scr.refresh()

    draw()
    while True:
        ch = scr.getch()
        if ch == 1: #Ctrl-A
            cursor = 0
        elif ch == 5: #Ctrl-E
            cursor = len(buf)
        elif ch == 21: #Ctrl-U
            buf = ""
            cursor = 0
            start = 0
        elif ch == curses.KEY_BACKSPACE:
            buf = buf[:cursor-1] + buf[cursor:]
            cursor -= 1
        elif ch == 10: #Enter
            return buf
        elif ch == curses.KEY_LEFT:
            cursor -= 1
        elif ch == curses.KEY_RIGHT:
            cursor += 1
        else:
            cursor+=1
            buf = buf[:cursor-1] + chr(ch) + buf[cursor-1:]

        if cursor < 0:
            cursor = 0
        if cursor > len(buf):
            cursor = len(buf)
        draw()
