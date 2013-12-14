syncboard
=========

An open source, cross-platform clipboard syncing tool

The intent is for a person using multiple computers concurrently to be able to
easily transfer the clipboard contents between them.

It currently works with two computers, but it will not work well with more than
two.

Running
=======

To run syncboard, go into the src directory, and run:

    python gui.py

Double clicking the gui.py file may also work, depending on your system's
configuration.

Testing
=======

Use nose to run the tests:

    nosetests

To include any debugging output from stdout, run:

    nosetests --nocapture

Dependencies
============
[Python 2.7](http://www.python.org/download/releases/2.7.6/)

[wxPython 2.8](http://www.wxpython.org/download.php)
