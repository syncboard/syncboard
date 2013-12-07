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
    This file is the user's entrance to the gui and implements the main frame
    of the gui.
"""

import wx, info
from wx.lib.pubsub import Publisher
from gui_info import AboutDialog
from gui_status import StatusPanel
from gui_clipboard import ClipboardPanel
from gui_connections import ConnectionsPanel
from session import Session

FRAME_SIZE = (500, 510)
BGD_COLOR = (240, 240, 240)

class MainFrame(wx.Frame):
    """Main Frame  of the app."""
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.session = Session()

        self.SetBackgroundColour(BGD_COLOR)

        # Build the menu bar
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, text="E&xit")
        self.Bind(wx.EVT_MENU, self.on_quit, exit_item)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, text="&About",
                                      help="Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        self.CreateStatusBar(style=0)
        Publisher().subscribe(self.change_statusbar, "change_statusbar")

        # Add panels
        connections_panel = ConnectionsPanel(self, self.session)
        clipboard_panel = ClipboardPanel(self)
        status_panel = StatusPanel(self)

        new_btn = wx.Button(self, label="New Connection")
        new_btn.Bind(wx.EVT_BUTTON, self.on_new)

        auto_sync_cb = wx.CheckBox(self, id=wx.ID_ANY,
                                       label="Automatically Sync")

        self.Bind(wx.EVT_CHECKBOX, self.on_toggle_auto, auto_sync_cb)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        board_sizer = wx.BoxSizer(wx.VERTICAL)

        btn_flags = wx.SizerFlags().Proportion(0).Border(wx.ALL, 5).Bottom()
        status_flags = wx.SizerFlags().Proportion(1).Expand().Border(wx.ALL, 5).Top()
        flags = wx.SizerFlags().Proportion(0).Expand().Border(wx.ALL, 5)
        board_flags = wx.SizerFlags().Proportion(0).Border(wx.ALL, 5).Right()
        top_flags = wx.SizerFlags().Proportion(0).Expand().Border(wx.ALL, 5)
        conn_flags = wx.SizerFlags().Proportion(1).Expand().Border(wx.ALL, 5)
        
        board_sizer.AddF(auto_sync_cb, flags)
        board_sizer.AddF(clipboard_panel, flags)

        top_row_sizer.AddF(new_btn, btn_flags)
        top_row_sizer.AddF(status_panel, status_flags)
        top_row_sizer.AddF(board_sizer, board_flags)

        main_sizer.AddF(top_row_sizer, top_flags)
        main_sizer.AddF(connections_panel, conn_flags)

        self.SetSizer(main_sizer)

    def change_statusbar(self, msg):
        self.SetStatusText(msg.data)

    def on_new(self, event):
        Publisher().sendMessage(("new_connection"))

    def on_toggle_auto(self, event):
        Publisher().sendMessage(("auto_toggle"), event.IsChecked())

    def on_about(self, event):
        aboutbox = AboutDialog(self)
        aboutbox.ShowModal()
        aboutbox.Destroy()

    def on_quit(self, event):
        self.Close()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, title=info.NAME, size=FRAME_SIZE,
                      style=wx.DEFAULT_FRAME_STYLE)# ^ wx.RESIZE_BORDER)
    frame.Show()
    app.MainLoop()
