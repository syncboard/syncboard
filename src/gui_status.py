"""
    Cross-platform clipboard syncing tool
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

import wx
from wx.lib.pubsub import Publisher
from info import TXT

class StatusPanel(wx.Panel):
    """This Panel is for managing options"""
    DEFAULT_COLOR = (0, 0, 0)
    OK_COLOR = (0, 200, 0)
    BAD_COLOR = (200, 0, 0)
    def __init__(self, parent, bgd_color, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.bgd_color = bgd_color
        self.SetBackgroundColour(self.bgd_color)

        title_font = wx.Font(pointSize=10,
                             family=wx.FONTFAMILY_DEFAULT,
                             style=wx.FONTSTYLE_NORMAL,
                             weight=wx.FONTWEIGHT_BOLD)

        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Status")
        title.SetFont(title_font)
        flags = wx.SizerFlags().Proportion(0)
        sizer.AddF(title, flags)

        local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self, label="Your Clipboard:")
        flags = wx.SizerFlags().Proportion(0)
        local_sizer.AddF(t, flags)

        self.local_type = wx.StaticText(self, label="Empty")
        flags.Border(wx.LEFT, 20).Right()
        local_sizer.AddF(self.local_type, flags)

        flags = wx.SizerFlags().Proportion(0).Border(wx.TOP, 10)
        sizer.AddF(local_sizer, flags)

        shared_sizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self, label="Shared Clipboard:")
        flags = wx.SizerFlags().Proportion(0)
        shared_sizer.AddF(t, flags)

        self.shared_type = wx.StaticText(self, label="Empty")
        flags.Border(wx.LEFT, 20).Right()
        shared_sizer.AddF(self.shared_type, flags)

        self.new = wx.StaticText(self, label="NEW")
        self.new.SetForegroundColour("green")
        flags = wx.SizerFlags().Proportion(0).Border(wx.LEFT, 10)
        shared_sizer.AddF(self.new, flags)

        flags = wx.SizerFlags().Proportion(0).Border(wx.TOP, 5)
        sizer.AddF(shared_sizer, flags)
        
        self.SetSizerAndFit(sizer)

        self.new.Hide()

        Publisher().subscribe(self.user_copy, "user_copy")
        Publisher().subscribe(self.user_paste, "user_paste")
        Publisher().subscribe(self.update_clipboard, "update_clipboard")
        Publisher().subscribe(self.update_shared_clipboard, "update_shared_clipboard")

        # Used to prevent "NEW" from poping up when the user pastes
        self.user_pasted = False

    def user_copy(self, msg):
        self.new.Hide()

    def user_paste(self, msg):
        self.new.Hide()
        self.user_pasted = True

    def update_clipboard(self, msg):
        data_type = msg.data
        self.local_type.SetLabel(data_type)
        if data_type == TXT:
            color = self.OK_COLOR
        else:
            color = self.BAD_COLOR

        self.local_type.SetForegroundColour(color)

    def update_shared_clipboard(self, msg):
        data_type = msg.data
        self.shared_type.SetLabel(data_type)
        if not self.user_pasted and data_type != "Empty":
            self.new.Show()
            print 'show'

        self.user_pasted = False

        # What happens if two version of the app support different data types
        # and are communicating? I would expect if the shared clipboard
        # contained data not supported by your version you wouldn't be able
        # to copy from it. If we need to handle this case then the code below
        # may become relevent.

        # if data_type == TXT:
        #     color = self.OK_COLOR
        # else:
        #     color = self.BAD_COLOR

        # self.local_type.SetForegroundColour(color)

