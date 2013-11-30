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
from wx.lib.pubsub import Publisher
from connections import MAX_ALIAS_LENGTH, Connection

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

class Row:
    DEFAULT_COLOR = (255, 255, 255)
    REQUEST_COLOR = (255, 255, 100)
    ACTIVE_COLOR = (100, 255, 100)
    def __init__(self, button, label, connection, line):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(button, proportion=0, flag=wx.ALL, border=5)
        self.sizer.Add(label,
                       proportion=0,
                       flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                       border=5)
        # TODO: Add accept/decline buttons for when pending
        
        self.button = button
        self.label = label
        self.connection = connection
        self.line = line
        self.color = self.DEFAULT_COLOR
        ### For testing:
        self.time = 0
        self.pending = 20
        self.connected = 50
        ###
        self.color = self.update_color()

    def update_color(self):
        if self.connection.status == Connection.PENDING:
            if self.color == self.DEFAULT_COLOR:
                self.color = self.REQUEST_COLOR
            else:
                self.color = self.DEFAULT_COLOR
        elif self.connection.status == Connection.CONNECTED:
            self.color = self.ACTIVE_COLOR
        elif self.connection.status == Connection.NOT_CONNECTED:
            self.color = self.DEFAULT_COLOR
        else:
            self.color = self.DEFAULT_COLOR

        # For testing:
        if self.time > self.connected:
            self.connection.status = Connection.NOT_CONNECTED
        elif self.time > self.pending:
            self.connection.status = Connection.CONNECTED
        else:
            self.connection.status = Connection.PENDING
        self.time += 1

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
                                 name="connection list")
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

        self.btn_to_row = {}

        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(500)

    def config_size(self):
        self.scroll_window.SetSizer(self.scroll_sizer)
        self.scroll_window.SetAutoLayout(1)
        self.scroll_window.SetupScrolling()

    def on_timer(self, event):
        for row in self.btn_to_row.values():
            row.update_color()
            row.label.SetBackgroundColour(row.color)
        self._rearange()
        self.Refresh()

    def on_new(self, event):
        new_box = NewConnectionDialog(self)
        if new_box.ShowModal() == wx.ID_OK:
            alias = new_box.alias.GetValue()
            addr = new_box.address.GetValue()
            self.session.new_connection(alias, addr)
            conn = self.session.get_connection(addr)
            
            name = addr
            if alias: name = alias
            
            rmv_btn = wx.Button(self.scroll_window, wx.ID_ANY, size=(20,20),
                                label="X")
            rmv_btn.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_remove)
            rmv_btn.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_remove)
            rmv_btn.Bind(wx.EVT_BUTTON, self.on_remove)

            label = wx.StaticText(self.scroll_window, label=name)
            line = wx.StaticLine(self.scroll_window)

            
            row = Row(rmv_btn, label, conn, line)
            self.btn_to_row[rmv_btn] = row
            
            self._add_row(row)

            self.config_size()
            
        new_box.Destroy()

    def on_enter_remove(self, event):
        msg = "Remove connection from list"
        Publisher().sendMessage(('change_statusbar'), msg)

    def on_leave_remove(self, event):
        Publisher().sendMessage(('change_statusbar'), "")

    def on_remove(self, event):
        btn = event.GetEventObject()
        row = self.btn_to_row[btn]
        self.scroll_sizer.Remove(row.sizer)
        
        row.button.Destroy()
        row.label.Destroy()
        row.line.Destroy()
        del self.btn_to_row[btn]

        self.config_size()

        self.session.del_connection(row.connection.address)

    def _rearange(self):
        self._clear_row_display()
        for row in sorted(self.btn_to_row.values(),
                          key=lambda r: r.connection.status, reverse=True):
            self._add_row(row)
        self.config_size()

    def _add_row(self, row):
        self.scroll_sizer.Add(row.sizer)
        self.scroll_sizer.Add(row.line, 0, wx.EXPAND)

    def _clear_row_display(self):
        for row in self.btn_to_row.values():
            self.scroll_sizer.Detach(row.sizer)
            self.scroll_sizer.Remove(row.line)
