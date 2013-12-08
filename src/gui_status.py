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
        flags.Border(wx.LEFT, 10)
        local_sizer.AddF(self.local_type, flags)

        flags = wx.SizerFlags().Proportion(0)
        sizer.AddF(local_sizer, flags)

        # self.new = wx.StaticText(self, label="NEW")
        # self.new.SetFont(title_font)
        # self.new.SetForegroundColour("green")
        # self.new.Hide()
        # flags = wx.SizerFlags().Proportion(1).Border(wx.LEFT, 10)
        # title_sizer.AddF(self.new, flags)

        # flags = wx.SizerFlags().Proportion(0).Border(wx.LEFT, 20)
        # sizer.AddF(title_sizer, flags)
        
        self.SetSizerAndFit(sizer)

        Publisher().subscribe(self.update_new, "auto_toggle")
        Publisher().subscribe(self.user_copy, "user_copy")
        Publisher().subscribe(self.user_paste, "user_paste")
        Publisher().subscribe(self.update_clipboard, "update_clipboard")

    def update_new(self, msg):
        state = msg.data
        if msg.data:
            self.new.Show()
        else:
            self.new.Hide()
        self.GetSizer().Layout()

    def user_copy(self, msg):
        print "user copy"

    def user_paste(self, msg):
        print "user paste"

    def update_clipboard(self, msg):
        data_type = msg.data
        self.local_type.SetLabel(data_type)
        if data_type == TXT:
            color = self.OK_COLOR
        else:
            color = self.BAD_COLOR

        self.local_type.SetForegroundColour(color)
