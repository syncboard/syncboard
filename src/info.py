"""
    Cross-platform clipboard sycning tool
    Copyright (C) 2013  Syncboard

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

"""
    This file contains information about the application itself.
"""

from os.path import join

f = open(join(".." + "/" + "LICENSE"), "r")
msg = f.read()
f.close()

LICENSE_TEXT = msg
DESCRIPTION_TEXT = "a cross-platform clipboard syncing tool"
      
NAME = "Syncboard"
VERSION = "0.0.0"
COPYRIGHT = "(C) 2013"
WEBSITE = ("https://github.com/syncboard/syncboard", "Source on Github")
DEVELOPERS = [ "Brandon Edgren", "Nat Mote"]

# Supported clipboard data types
TXT = "Text"
#BMP = "Bitmap"
