Goals
=====

A collection of curses utils for performing simple UI tasks. Currently
this includes a simple console and a menu with vi-like bindings.

Installation
============

Requires python 3.

``pip3 install curses-util`` should do the trick, or else
``python setup.py install`` from source.

Usage
=====

SimpleConsole
-------------

A simple console with a single line input window.

::

        import curses_util

        def handle_input(console, input):
            console.log("Got input: " + input) #Logs result to the output window.

        console = curses_used.SimpleConsole(handle_input)
        console.log("Welcome")

Menu
----

This can be used to vend a collection of items which the user may then
select one or more of. Navigation can be performed using standard vi
bindings (count operands are also supported) or via the arrow keys.
Multiple items can be selected with 'multi\_vend()' if the user presses
m over each of the items they wish to select and then presses enter.

::

        import curses_util

        menu = curses_util.Menu()

        items = [ str(i) for i in range(100) ]
        selected = menu.vend(items)

        print("The following items were selected: \n")
        print("\n".join(items), "\n")

Bugs, etc..
===========

If you bother to read the code and invariably feel the need to abuse the
person who wrote it, know that such sentiments will be happily received
at r.vaiya@gmail.com.
