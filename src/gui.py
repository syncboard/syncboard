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
from gui_connections import ConnectionsPanel
from session import Session

FRAME_SIZE = (500, 510)

# TODO: move options and display to their own files

class OptionsPanel(wx.Panel):
    """This Panel is for managing options"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

##        self.hotkey_cb = wx.CheckBox(self, id=wx.ID_ANY,
##                                     label="Enable Shortcut Keys (Ctrl+Shift+C/V)")
##        self.hotkey_cb.SetValue(True)
##        self.auto_sync_cb = wx.CheckBox(self, id=wx.ID_ANY,
##                                       label="Automatically Sync")

##        self.Bind(wx.EVT_CHECKBOX, self.on_check_box, self.hotkey_cb)
##        self.Bind(wx.EVT_CHECKBOX, self.on_check_box, self.auto_sync_cb)

        sizer = wx.BoxSizer(wx.VERTICAL)
##        sizer.Add(self.hotkey_cb, proportion=0, flag=wx.ALL, border=10)
##        sizer.Add(self.auto_sync_cb, proportion=0, flag=wx.ALL, border=10)
        t = wx.StaticText(self, label="Status")
        sizer.Add(t)
        self.SetSizerAndFit(sizer)

    def on_check_box(self, event):
        cb = event.GetEventObject()
        if cb == self.hotkey_cb:
            print "hotkey: ", event.IsChecked()
        elif cb == self.auto_sync_cb:
            print "auto: ", event.IsChecked()

        
class ClipboardPanel(wx.Panel):
    """
    This Panel is where the user copies and pastes. (it will also be for
    displaying clipboard contents if we choose to do so)
    """
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.TextCtrl(self, size=(150, 50),
                                style=wx.TE_CENTER | wx.TE_MULTILINE | wx.TE_NO_VSCROLL,
                                value="\nCopy/Paste Here")
        sizer.Add(self.text)

        self.SetSizerAndFit(sizer)

##        self.Bind(wx.EVT_IDLE, self.check_clipboard)
        self.Bind(wx.EVT_TEXT_PASTE, self.new_paste)
        self.Bind(wx.EVT_TEXT, self.reset)

        self.prev_content = ""
        self.dont_reset = False

    def new_paste(self, event):
        print "new paste"
        self.reset(None)

    def reset(self, event):
        if self.dont_reset:
            self.dont_reset = False
        else:
            self.dont_reset = True
            self.text.SetValue("Paste here")

    def check_clipboard(self, event):
        if not wx.TheClipboard.IsOpened():
            do = wx.TextDataObject()
            wx.TheClipboard.Open()
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if success:
                text = do.GetText()
                if text != self.prev_content:
                    print "New clipboard content"
                    self.text.SetValue(text)
                    self.prev_content = text
            else:
                self.text.SetValue("There is no data in the clipboard in the required format")


class MainFrame(wx.Frame):
    """Main Frame  of the app."""
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.session = Session()

        self.SetBackgroundColour((240, 240, 240))

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
        status_panel = OptionsPanel(self)

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
        if event.IsChecked():
            print "auto sync on"
        else:
            print "auto sync off"
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
