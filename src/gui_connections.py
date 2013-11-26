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
    This file contains gui elements for dealing with connections.
"""

import wx
import wx.lib.scrolledpanel as scrolled
from connections import MAX_ALIAS_LENGTH

CON_PANEL_WIDTH = 140
CON_PANEL_HEIGHT_OFFSET = 115 # subtracted from its containers height

class NewConnectionDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "New Connection")

        self.alias_label = wx.StaticText(self, wx.ID_ANY, "Alias (optional):")
        self.alias = wx.TextCtrl(self)
        self.alias.SetMaxLength(MAX_ALIAS_LENGTH)

        self.address_label = wx.StaticText(self, wx.ID_ANY, "Address:")
        self.address = wx.TextCtrl(self)
        self.address.SetMaxLength(15)
        
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_btn = wx.Button(self, wx.ID_OK, "OK")

        sizer = wx.GridBagSizer(3, 2)
        sizer.Add(self.alias_label,
                  pos=(0,0),
                  flag=wx.ALL,
                  border=5)
        sizer.Add(self.alias,
                  pos=(0,1),
                  flag=wx.ALL,
                  border=5)
        sizer.Add(self.address_label,
                  pos=(1,0),
                  flag=wx.ALL,
                  border=5)
        sizer.Add(self.address,
                  pos=(1,1),
                  flag=wx.ALL,
                  border=5)
        sizer.Add(cancel_btn,
                  pos=(2,0),
                  flag= wx.ALIGN_CENTER | wx.ALL,
                  border=5)
        sizer.Add(ok_btn,
                  pos=(2,1),
                  flag= wx.ALIGN_CENTER | wx.ALL,
                  border=5)        
        
        self.SetSizerAndFit(sizer)
        self.Center(wx.BOTH)

class ConnectionsPanel(wx.Panel):
    """This Panel is for managing and displaying connections"""
    def __init__(self, parent, session, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.session = session

        new_btn = wx.Button(self, label="New Connection")
        new_btn.Bind(wx.EVT_BUTTON, self.on_new)

        height = parent.GetSize()[1] - CON_PANEL_HEIGHT_OFFSET
        self.scroll_window = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                 size=(CON_PANEL_WIDTH, height),
                                 style = wx.SUNKEN_BORDER,
                                 name="connection list" )
        self.scroll_window.SetBackgroundColour("WHITE")
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.config_size()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(new_btn,
                       proportion=0,
                       flag=wx.EXPAND | wx.ALL,
                       border=5)
        self.sizer.Add(self.scroll_window,
                       proportion=0,
                       flag=wx.FIXED_MINSIZE | wx.ALL,
                       border=5)

        self.SetSizerAndFit(self.sizer)

    def config_size(self):
        self.scroll_window.SetSizer(self.scroll_sizer)
        self.scroll_window.SetAutoLayout(1)
        self.scroll_window.SetupScrolling()

    def on_new(self, event):
        new_box = NewConnectionDialog(self)
        if new_box.ShowModal() == wx.ID_OK:
            self.session.new_connection(new_box.alias.GetValue(),
                                        new_box.address.GetValue())

            btn = wx.Button(self.scroll_window, label="Remove")
            btn.Bind(wx.EVT_BUTTON, self.on_remove)
            self.scroll_sizer.Add(btn, proportion=0, flag=wx.ALL, border=5)

            self.config_size()
            
        new_box.Destroy()

    def on_remove(self, event):
        # TODO: remove connection from session
        btn = event.GetEventObject()
        self.scroll_sizer.Remove(btn)
        btn.Destroy()

        self.config_size()
