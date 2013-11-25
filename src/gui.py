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

import wx, info

class ConnectionsPanel(wx.Panel):
    """This Panel is for managing and displaying connections"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        new_btn = wx.Button(self, label="New Connection")
        new_btn.Bind(wx.EVT_BUTTON, self.on_new_connection)
        
        text = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(new_btn,
                  proportion=0,
                  flag=wx.EXPAND | wx.ALL,
                  border=5)
        sizer.Add(text,
                  proportion=1,
                  flag=wx.ALIGN_LEFT | wx.EXPAND | wx.ALL,
                  border=5)

        self.SetSizerAndFit(sizer)

    def on_new_connection(self, event):
        pass

class OptionsPanel(wx.Panel):
    """This Panel is for managing options"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.hotkey_cb = wx.CheckBox(self, id=wx.ID_ANY,
                                    label="Enable Shortcut Keys (Ctrl+Shift+C/V)")
        self.hotkey_cb.SetValue(True)
        self.auto_sync_cb = wx.CheckBox(self, id=wx.ID_ANY,
                                       label="Automatically Sync")

        self.Bind(wx.EVT_CHECKBOX, self.on_check_box, self.hotkey_cb)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_box, self.auto_sync_cb)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.hotkey_cb, proportion=0, flag=wx.ALL, border=10)
        sizer.Add(self.auto_sync_cb, proportion=0, flag=wx.ALL, border=10)

        self.SetSizerAndFit(sizer)

    def on_check_box(self, event):
        cb = event.GetEventObject()
        if cb == self.hotkey_cb:
            print "hotkey: ", event.IsChecked()
        elif cb == self.auto_sync_cb:
            print "auto: ", event.IsChecked()

        
class DisplayPanel(wx.Panel):
    """
    This Panel is where the user copies and pastes. (it will also be for
    displaying clipboard contents if we choose to do so)
    """
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        text = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(sizer)


class MainFrame(wx.Frame):
    """Main Frame  of the app."""
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # Build the menu bar
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, text="E&xit")
        self.Bind(wx.EVT_MENU, self.on_quit, exit_item)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, text="&About", help="Information about this program")
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        self.CreateStatusBar()

        # Add panels
        self.connections_panel = ConnectionsPanel(self, size=(300,300))
        self.display_panel = DisplayPanel(self)
        self.options_panel = OptionsPanel(self)

        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.sizer_h.Add(self.connections_panel,
                         proportion=0,
                         flag=wx.EXPAND,
                         border=5)
        self.sizer_h.Add(self.sizer_v,
                         proportion=1,
                         flag=wx.EXPAND,
                         border=5)
        self.sizer_v.Add(self.options_panel,
                         proportion=0,
                         flag=wx.EXPAND,
                         border=5)
        self.sizer_v.Add(self.display_panel,
                         proportion=1,
                         flag=wx.EXPAND,
                         border=5)

        self.SetSizer(self.sizer_h)
        self.SetAutoLayout(1)
##        self.sizer_h.Fit(self) # Maybe use this when all panels have content

    def on_about(self, event):
        aboutbox = info.AboutDialog(self)
        aboutbox.ShowModal()
        aboutbox.Destroy()

    def on_quit(self, event):
        self.Close()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, title=info.NAME, size=(500, 500))
    frame.Show()
    app.MainLoop()
