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

CON_PANEL_WIDTH = 285
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

class ConnectionWindow(wx.Panel):
    """This Panel is individual connections"""
    DEFAULT_COLOR = (255, 255, 255)
    REQUEST_COLOR = (255, 255, 100)
    CONNECT_COLOR = (100, 255, 100)
    def __init__(self, parent, connection, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.connection = connection
        
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.rmv_btn = wx.Button(self, wx.ID_ANY, size=(20,20), label="X")
        self.rmv_btn.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_remove)
        self.rmv_btn.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_remove)
        self.rmv_btn.Bind(wx.EVT_BUTTON, self.on_remove)
        self.sizer.Add(self.rmv_btn, proportion=0, flag=wx.ALL, border=5)

        size = (MAX_ALIAS_LENGTH * 8, 13)
        name = self.connection.address
        if self.connection.alias: name = self.connection.alias
        self.label = wx.StaticText(self, size=size, label=name)
        self.sizer.Add(self.label,
                       proportion=0,
                       flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                       border=5)

        self.state = None
        self.buttons = {}
        def add_button(label, size, callback):
            button = wx.Button(self, wx.ID_ANY,
                               size=size, label=label)
            button.Bind(wx.EVT_BUTTON, callback)
            self.sizer.Add(button, proportion=0, flag=wx.ALL, border=5)
            button.Hide()
            self.buttons[label] = button

        size = (50, 20)
        add_button("Accept", size, self.on_accept)
        add_button("Reject", size, self.on_remove)

        size = (100, 20)
        add_button("Connect", size, self.on_connect)
        self.spacer = True # Used for bug fix later

        size = (100, 20)
        add_button("Disconnect", size, self.on_disconnect)        

        self.sizer_v.Add(self.sizer)
        
        self.line = wx.StaticLine(self)
        self.sizer_v.Add(self.line, 0, wx.EXPAND)

        self.SetSizerAndFit(self.sizer_v)

        self.state_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_update_state, self.state_timer)
        self.state_timer.Start(100)

        self.color_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_update_color, self.color_timer)
        self.color_timer.Start(400)

### For testing:
        if self.connection.status == Connection.REQUEST:
            self.time = -1
        else:
            self.time = 0
###
        
    def get_sizer(self):
        return self.sizer_v

    def on_enter_remove(self, event):
        msg = "Remove connection from list"
        Publisher().sendMessage(("change_statusbar"), msg)

    def on_leave_remove(self, event):
        Publisher().sendMessage(("change_statusbar"), "")

    def on_remove(self, event):
        Publisher().sendMessage(("change_statusbar"), "")
        Publisher().sendMessage(("remove_connection"), self)

    def on_accept(self, event):
        Publisher().sendMessage(("accept_connection"), self)

    def on_connect(self, event):
##        Publisher().sendMessage(("reconnect"), self)
        print "reconnect"

    def on_disconnect(self, event):
##        Publisher().sendMessage(("disconnect"), self)
        print "disconect"

    def on_update_state(self, event):
        def hide_buttons():
            for b in self.buttons.values():
                b.Hide()

        def show_accept_reject():
            hide_buttons()
            self.buttons["Accept"].Show()
            self.buttons["Reject"].Show()

        def show_connect():
            hide_buttons()
            self.buttons["Connect"].Show()

        def show_disconnect():
            hide_buttons()
            self.buttons["Disconnect"].Show()
            
        if self.state == None:
            if self.connection.status == Connection.REQUEST:
                show_accept_reject()
            elif self.connection.status == Connection.NOT_CONNECTED:
                show_connect()
            elif self.connection.status == Connection.CONNECTED:
                show_disconnect()
        elif self.state == Connection.NOT_CONNECTED:
            if self.connection.status == Connection.REQUEST:
                show_accept_reject()
            elif self.connection.status == Connection.CONNECTED:
                show_disconnect()
            elif self.connection.status == Connection.PENDING:
                hide_buttons()
        elif self.state == Connection.CONNECTED:
            if self.connection.status == Connection.NOT_CONNECTED:
                show_connect()
### Fix for a really wierd bug: Connect button not positioned properly
                if self.spacer:
                    self.sizer.AddSpacer((10,20))
                    self.spacer = False
###
        elif self.state == Connection.PENDING:
            if self.connection.status == Connection.CONNECTED:
                show_disconnect()
            elif self.connection.status == Connection.NOT_CONNECTED:
                show_connect()
        elif self.state == Connection.REQUEST:
            if self.connection.status == Connection.CONNECTED:
                show_disconnect()
            elif self.connection.status == Connection.NOT_CONNECTED:
                show_connect()
        else:
            pass
        
        self.state = self.connection.status
        self.SetSizerAndFit(self.sizer_v)

    def on_update_color(self, event):
        if (self.connection.status == Connection.PENDING or
            self.connection.status == Connection.REQUEST):
            if self.label.GetBackgroundColour() == self.DEFAULT_COLOR:
                self.label.SetBackgroundColour(self.REQUEST_COLOR)
            else:
                self.label.SetBackgroundColour(self.DEFAULT_COLOR)
        elif self.connection.status == Connection.CONNECTED:
            self.label.SetBackgroundColour(self.CONNECT_COLOR)
        elif self.connection.status == Connection.NOT_CONNECTED:
            self.label.SetBackgroundColour(self.DEFAULT_COLOR)
        else:
            self.label.SetBackgroundColour(self.DEFAULT_COLOR)

### For testing:
        if self.time > 100:
            self.connection.status = Connection.NOT_CONNECTED
        elif self.time > 90:
            self.connection.status = Connection.PENDING
        elif self.time > 80:
            self.connection.status = Connection.CONNECTED
        elif self.time > 70:
            self.connection.status = Connection.REQUEST
        elif self.time > 60:
            self.connection.status = Connection.NOT_CONNECTED
        elif self.time > 50:
            self.connection.status = Connection.REQUEST
        elif self.time > 40:
            self.connection.status = Connection.NOT_CONNECTED
        elif self.time > 30:
            self.connection.status = Connection.CONNECTED
        elif self.time > 20:
            self.connection.status = Connection.NOT_CONNECTED
        elif self.time > 10:
            self.connection.status = Connection.CONNECTED
        elif self.time > 0:
            self.connection.status = Connection.PENDING
        if self.time >= 0:
            self.time += 1
###
        self.Refresh()

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
                       flag=wx.CENTER | wx.ALL,
                       border=5)
        self.sizer.Add(self.scroll_window,
                       proportion=0,
                       flag=wx.FIXED_MINSIZE | wx.ALL,
                       border=5)

        self.SetSizerAndFit(self.sizer)

        Publisher().subscribe(self.accept_connection, "accept_connection")
        Publisher().subscribe(self.remove_connection, "remove_connection")

        self.sync_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_sync, self.sync_timer)
        self.sync_timer.Start(200)

        self.known_connections = set()

### For testing
        self.new_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_new_timer, self.new_timer)
        self.new_timer.Start(1000)

    def on_new_timer(self, event):
        from random import randint
        if randint(1, 5) == 1:
            addr = str(randint(5000, 1000000))
            self.session.new_connection("", addr)
            c = self.session.get_connection(addr)
            c.status = Connection.REQUEST
###

    def on_sync(self, event):
        for connection in self.session.connections():
            if connection not in self.known_connections:
                self.add_connection(connection)

    def config_size(self):
        self.scroll_window.SetSizer(self.scroll_sizer)
        self.scroll_window.SetAutoLayout(1)
        self.scroll_window.SetupScrolling()

    def on_new(self, event):
        new_box = NewConnectionDialog(self)
        if new_box.ShowModal() == wx.ID_OK:
            alias = new_box.alias.GetValue()
            addr = new_box.address.GetValue()
            self.session.new_connection(alias, addr)
            conn = self.session.get_connection(addr)

            self.add_connection(conn)
            
        new_box.Destroy()

    def add_connection(self, conn):
        self.known_connections.add(conn)
        row = ConnectionWindow(self.scroll_window, conn)
        self.scroll_sizer.Add(row)
        self.config_size()

    def remove_connection(self, msg):
        conn_window = msg.data
        self.scroll_sizer.Remove(conn_window.get_sizer())
        conn = conn_window.connection
        addr = conn.address
        conn_window.Destroy()

        self.known_connections.remove(conn)
        
        self.config_size()
        self.session.del_connection(addr)

    def accept_connection(self, msg):
        conn = msg.data.connection
        self.session.accept_connection(conn.address)
##
##    def _rearange(self):
##        self._clear_row_display()
##        for row in sorted(self.btn_to_row.values(),
##                          key=lambda r: r.connection.status, reverse=True):
##            self._add_row(row)
##        self.config_size()
##
##    def _add_row(self, row):
##        self.scroll_sizer.Add(row.sizer)
##        self.scroll_sizer.Add(row.line, 0, wx.EXPAND)
##
##    def _clear_row_display(self):
##        for row in self.btn_to_row.values():
##            self.scroll_sizer.Detach(row.sizer)
##            self.scroll_sizer.Remove(row.line)
