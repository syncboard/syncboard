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

"""
    This file contains gui elements for dealing with connections.
"""

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.stattext as st
from wx.lib.pubsub import Publisher
from connections import MAX_ALIAS_LENGTH, MAX_ADDRESS_LENGTH, Connection


class NewConnectionDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "New Connection")

        # Declaring alias first to preserve tab order
        self.alias_label = wx.StaticText(self, wx.ID_ANY, "Alias (optional):")
        self.alias = wx.TextCtrl(self)

        self.address_label = wx.StaticText(self, wx.ID_ANY, "IPv4 Address:")
        self.address = wx.TextCtrl(self)
        self.address.SetMaxLength(MAX_ADDRESS_LENGTH)
        width, height = self.address.GetSizeTuple()
        char_width = 8
        width = MAX_ADDRESS_LENGTH * char_width
        self.address.SetMinSize((width, height))
        self.Bind(wx.EVT_TEXT, self.on_edit_address, self.address)

        self.alias.SetMaxLength(MAX_ALIAS_LENGTH)
        self.alias.SetMinSize((width, height))
        
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.ok_btn = wx.Button(self, wx.ID_OK, "OK")
        self.ok_btn.Disable()
        self.ok_btn.SetDefault()

        flags = wx.SizerFlags().Border(wx.ALL, 5)
        
        sizer = wx.FlexGridSizer(3, 2)
        
        sizer.AddF(self.alias_label, flags=flags)
        sizer.AddF(self.alias, flags=flags)
        sizer.AddF(self.address_label, flags=flags)
        sizer.AddF(self.address, flags=flags)
        sizer.AddF(cancel_btn, flags=flags)
        sizer.AddF(self.ok_btn, flags=flags)       
        
        self.SetSizerAndFit(sizer)
        self.Center(wx.BOTH)

    def on_edit_address(self, event):
        import re
        address_pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if address_pattern.match(self.address.GetValue()):
            self.address.SetForegroundColour((0, 140, 0))
            self.ok_btn.Enable()
        else:
            self.address.SetForegroundColour((140, 0, 0))
            self.ok_btn.Disable()
        self.address.Refresh()


class EditAliasDialog(wx.Dialog):
    def __init__(self, parent, current_alias, address):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit Alias")

        self.alias_label = wx.StaticText(self, wx.ID_ANY, "Alias:")
        self.alias = wx.TextCtrl(self)
        self.alias.SetValue(current_alias)
        self.alias.SetMaxLength(MAX_ALIAS_LENGTH)

        width, height = self.alias.GetSizeTuple()
        char_width = 8
        width = MAX_ADDRESS_LENGTH * char_width
        self.alias.SetMinSize((width, height))

        self.address_label = wx.StaticText(self, wx.ID_ANY, "IPv4 Address:")
        self.address = wx.StaticText(self, wx.ID_ANY, address)

        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.ok_btn = wx.Button(self, wx.ID_OK, "OK")
        self.ok_btn.SetDefault()

        flags = wx.SizerFlags().Border(wx.ALL, 5)
        
        sizer = wx.FlexGridSizer(3, 2)
        
        sizer.AddF(self.alias_label, flags=flags)
        sizer.AddF(self.alias, flags=flags)
        sizer.AddF(self.address_label, flags=flags)
        sizer.AddF(self.address, flags=flags)
        sizer.AddF(cancel_btn, flags=flags)
        sizer.AddF(self.ok_btn, flags=flags)       
        
        self.SetSizerAndFit(sizer)
        self.Center(wx.BOTH)


class ConnectionWindow(wx.Panel):
    """This Panel is individual connections"""
    DEFAULT_COLOR = (240, 240, 240)
    REQUEST_COLOR = (255, 255, 100)
    CONNECT_COLOR = (100, 255, 100)
    def __init__(self, parent, connection, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.connection = connection
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.rmv_btn = wx.Button(self, wx.ID_ANY, size=(20,20), label="X")
        self.rmv_btn.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_remove)
        self.rmv_btn.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_remove)
        self.rmv_btn.Bind(wx.EVT_BUTTON, self.on_remove)
        flags = wx.SizerFlags().Proportion(0).Border(wx.ALL, 5)
        self.sizer.AddF(self.rmv_btn, flags)

        size = (MAX_ALIAS_LENGTH * 8, 13)
        name = self.connection.address
        if self.connection.alias: name = self.connection.alias
        self.label = wx.TextCtrl(self, style=wx.TE_READONLY | wx.NO_BORDER)
        self.label.SetValue(name)
        self.label.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.label.SetBackgroundColour(self.GetBackgroundColour())
        self.label.Bind(wx.EVT_LEFT_DOWN, self.on_click_label)
        self.label.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_label)
        self.label.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_label)
        flags = wx.SizerFlags().Proportion(1).Expand().Border(wx.ALL, 5)
        flags.Align(wx.ALIGN_CENTER_VERTICAL)
        self.sizer.AddF(self.label, flags)

        self.state = None
        self.buttons = {}
        def add_button(label, callback):
            button = wx.Button(self, wx.ID_ANY,
                               label=label)
            button.Bind(wx.EVT_BUTTON, callback)
            flags = wx.SizerFlags().Proportion(0).Border(wx.ALL, 5)
            flags.Align(wx.ALIGN_CENTER_VERTICAL)
            self.sizer.AddF(button, flags)
            button.Hide()
            self.buttons[label] = button

        add_button("Accept", self.on_accept)
        add_button("Reject", self.on_remove)

        add_button("Connect", self.on_connect)

        add_button("Disconnect", self.on_disconnect)

        waiting = wx.StaticText(self, label="Request pending...")
        flags = wx.SizerFlags().Proportion(0).Border(wx.ALL, 5)
        flags.Align(wx.ALIGN_CENTER_VERTICAL)
        self.sizer.AddF(waiting, flags)
        waiting.Hide()
        self.buttons["Waiting"] = waiting

        add_button("Cancel", self.on_cancel)

        self.SetSizerAndFit(self.sizer)

        self.state_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_update_state, self.state_timer)
        self.state_timer.Start(100)

        self.color_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_update_color, self.color_timer)
        self.color_timer.Start(400)

        self.initSize = self.GetMinSize()

### For testing:
        # if self.connection.status == Connection.REQUEST:
        #     self.time = -1
        # else:
        #     self.time = 0
###

    def get_sizer(self):
        return self.sizer

    def on_enter_remove(self, event):
        msg = "Remove connection from list"
        Publisher().sendMessage(("change_statusbar"), msg)
        event.Skip()

    def on_leave_remove(self, event):
        Publisher().sendMessage(("change_statusbar"), "")
        event.Skip()

    def on_remove(self, event):
        Publisher().sendMessage(("change_statusbar"), "")
        Publisher().sendMessage(("remove_connection"), self)

    def on_enter_label(self, event):
        msg = "Edit alias"
        Publisher().sendMessage(("change_statusbar"), msg)
        event.Skip()

    def on_leave_label(self, event):
        Publisher().sendMessage(("change_statusbar"), "")
        event.Skip()

    def on_click_label(self, event):
        Publisher().sendMessage(("edit_alias"), self)

    def on_accept(self, event):
        Publisher().sendMessage(("accept_connection"), self)

    def on_connect(self, event):
        Publisher().sendMessage(("reconnect"), self)

    def on_disconnect(self, event):
        Publisher().sendMessage(("disconnect"), self)

    def on_cancel(self, event):
        Publisher().sendMessage(("cancel"), self)

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

        def show_waiting():
            hide_buttons()
            self.buttons["Waiting"].Show()
            self.buttons["Cancel"].Show()
            
        if self.state == None:
            if self.connection.status == Connection.PENDING:
                show_waiting()
            elif self.connection.status == Connection.REQUEST:
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
                show_waiting()
        elif self.state == Connection.CONNECTED:
            if self.connection.status == Connection.NOT_CONNECTED:
                show_connect()
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
        self.sizer.Layout()

    def on_update_color(self, event):
        change = self
        if (self.connection.status == Connection.PENDING or
            self.connection.status == Connection.REQUEST):
            if change.GetBackgroundColour() == self.DEFAULT_COLOR:
                change.SetBackgroundColour(self.REQUEST_COLOR)
            else:
                change.SetBackgroundColour(self.DEFAULT_COLOR)
        elif self.connection.status == Connection.CONNECTED:
            change.SetBackgroundColour(self.CONNECT_COLOR)
        elif self.connection.status == Connection.NOT_CONNECTED:
            change.SetBackgroundColour(self.DEFAULT_COLOR)
        else:
            change.SetBackgroundColour(self.DEFAULT_COLOR)

        self.label.SetBackgroundColour(self.GetBackgroundColour())

### For testing:
        # if self.time > 100:
        #     self.connection.status = Connection.NOT_CONNECTED
        # elif self.time > 90:
        #     self.connection.status = Connection.PENDING
        # elif self.time > 80:
        #     self.connection.status = Connection.CONNECTED
        # elif self.time > 70:
        #     self.connection.status = Connection.REQUEST
        # elif self.time > 60:
        #     self.connection.status = Connection.NOT_CONNECTED
        # elif self.time > 50:
        #     self.connection.status = Connection.REQUEST
        # elif self.time > 40:
        #     self.connection.status = Connection.NOT_CONNECTED
        # elif self.time > 30:
        #     self.connection.status = Connection.CONNECTED
        # elif self.time > 20:
        #     self.connection.status = Connection.NOT_CONNECTED
        # elif self.time > 10:
        #     self.connection.status = Connection.CONNECTED
        # elif self.time > 0:
        #     self.connection.status = Connection.PENDING
        # if self.time >= 0:
        #     self.time += 1
###
        self.Refresh()

class ConnectionsPanel(wx.Panel):
    """This Panel is for managing and displaying connections"""
    def __init__(self, parent, session, bgd_color, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.session = session

        self.bgd_color = bgd_color

        self.SetBackgroundColour(self.bgd_color)

        self.scroll_window = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                 style = wx.SUNKEN_BORDER,
                                 name="connection list")
        self.scroll_window.SetBackgroundColour(self.bgd_color)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.config_size()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        flags = wx.SizerFlags().Proportion(1).Expand().Border(wx.ALL, 5)
        self.sizer.AddF(self.scroll_window, flags)

        self.SetSizerAndFit(self.sizer)

        Publisher().subscribe(self.new_connection, "new_connection")
        Publisher().subscribe(self.accept_connection, "accept_connection")
        Publisher().subscribe(self.remove_connection, "remove_connection")
        Publisher().subscribe(self.request_connection, "reconnect")
        Publisher().subscribe(self.disconnect, "disconnect")
        Publisher().subscribe(self.cancel_request, "cancel")
        Publisher().subscribe(self.edit_alias, "edit_alias")

        self.sync_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_sync, self.sync_timer)
        self.sync_timer.Start(200)
        Publisher().sendMessage(("new_timer"), self.sync_timer)

        self.sort_timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_sort, self.sort_timer)
        self.sort_timer.Start(500)
        Publisher().sendMessage(("new_timer"), self.sort_timer)

        self.rows = set()
        self.known_connections = set()

### For testing
    #     self.new_timer = wx.Timer(self, wx.ID_ANY)
    #     self.Bind(wx.EVT_TIMER, self.on_new_timer, self.new_timer)
    #     self.new_timer.Start(1000)

    # def on_new_timer(self, event):
    #     from random import randint
    #     if randint(1, 5) == 1:
    #         addr = str(randint(5000, 1000000))
    #         self.session.new_connection("", addr)
    #         c = self.session.get_connection(addr)
    #         c.status = Connection.REQUEST
###

    def on_sync(self, event):
        for connection in self.session.connections():
            if connection not in self.known_connections:
                self.add_connection(connection)

    def config_size(self):
        self.scroll_window.SetSizer(self.scroll_sizer)
        self.scroll_window.SetupScrolling(scrollToTop=False)

    def new_connection(self, msg):
        new_box = NewConnectionDialog(self)
        new_box.SetBackgroundColour(self.bgd_color)
        if new_box.ShowModal() == wx.ID_OK:
            alias = new_box.alias.GetValue()
            addr = new_box.address.GetValue()
            self.session.new_connection(alias, addr)
            conn = self.session.get_connection(addr)

        new_box.Destroy()

    def _add_row_to_sizer(self, row):
        flags = wx.SizerFlags().Expand()
        self.scroll_sizer.AddF(row, flags)
        
    def add_connection(self, conn):
        self.known_connections.add(conn)
        row = ConnectionWindow(self.scroll_window, conn, style=wx.RAISED_BORDER)
        row.SetBackgroundColour(self.bgd_color)
        self.rows.add(row)

        self._add_row_to_sizer(row)
        self.config_size()

    def remove_connection(self, msg):
        row = msg.data
        self.scroll_sizer.Remove(row.get_sizer())
        conn = row.connection
        addr = conn.address
        
        self.rows.remove(row)
        row.Destroy()
        
        self.known_connections.remove(conn)
        
        self.config_size()
        self.session.del_connection(addr)

    def accept_connection(self, msg):
        conn = msg.data.connection
        self.session.accept_connection(conn.address)

    def request_connection(self, msg):
        conn = msg.data.connection
        self.session.request_connection(conn.address)

    def disconnect(self, msg):
        conn = msg.data.connection
        self.session.disconnect(conn.address)

    def cancel_request(self, msg):
        conn = msg.data.connection
        self.session.cancel_request(conn.address)

    def edit_alias(self, msg):
        conn = msg.data.connection
        current_alias = conn.alias
        address = conn.address

        edit_box = EditAliasDialog(self, current_alias, address)
        edit_box.SetBackgroundColour(self.bgd_color)

        if edit_box.ShowModal() == wx.ID_OK:
            new_alias = edit_box.alias.GetValue()
            self.session.update_alias(conn.address, new_alias)
            msg.data.label.SetValue(new_alias)

        edit_box.Destroy()

    def on_sort(self, event):
        for row in self.rows:
            self.scroll_sizer.Detach(row)            
        
        for row in sorted(self.rows,
                          key=lambda r: r.connection.status, reverse=True):
            self._add_row_to_sizer(row)
             
        self.config_size()

