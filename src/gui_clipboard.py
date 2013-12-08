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

class ClipboardPanel(wx.Panel):
    """
    This Panel is where the user copies and pastes. (it will also be for
    displaying clipboard contents if we choose to do so)
    """
    DEFAULT_COLOR = (0, 0, 0)
    OK_COLOR = (0, 200, 0)
    BAD_COLOR = (200, 0, 0)
    def __init__(self, parent, session, bgd_color, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.session = session

        self.bgd_color = bgd_color
        self.SetBackgroundColour(self.bgd_color)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.TextCtrl(self, size=(150, 50),
                        style=wx.TE_CENTER | wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        self.text.SetBackgroundColour(self.bgd_color)
        sizer.Add(self.text)

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_IDLE, self.check_clipboard)
        self.has_valid_data = False

        self.Bind(wx.EVT_TEXT, self.on_edit)
        self.Bind(wx.EVT_TEXT_COPY, self.on_copy)
        self.Bind(wx.EVT_TEXT_PASTE, self.on_paste)

        self.text.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.on_unfocus)
        self.has_focus = False

        Publisher().subscribe(self.auto_toggle, "auto_toggle")
        self.auto_sync = False

        # For preveting mex recursion depth on Linux
        self.setting_message = True
        self.text.SetValue("Copy/Paste Here")
        self.setting_message = False

        self.local_prev = ""
        self.local_prev_type = "Uknown"
        text_obj = wx.TextDataObject()
        wx.TheClipboard.Open()
        contains_text = wx.TheClipboard.GetData(text_obj)
        wx.TheClipboard.Close()
        if contains_text:
            self.local_prev = text_obj.GetText()

### For testing
    #     self.test_timer = wx.Timer(self, wx.ID_ANY)
    #     self.Bind(wx.EVT_TIMER, self.on_test_timer, self.test_timer)
    #     self.test_timer.Start(5000)

    # def on_test_timer(self, event):
    #     import random, string
    #     text = "".join([random.choice(string.letters) for i in xrange(random.randint(10, 50))])
    #     conns = self.session.connections()
    #     if conns:
    #         sender = random.choice(conns)
    #         self.session.set_clipboard_data(text, TXT)
    #         self.session._data_owner = sender
    #         print "new data from %s" % sender.address
###

    def _set_message(self):
        self.setting_message = True
        if self.auto_sync:
            self.text.SetValue("\nAuto Sync")
        else:
            if self.has_focus:
                if self.has_valid_data:
                    self.text.SetValue("Copy/Paste Here\nReady")
                    self.text.SetForegroundColour(self.OK_COLOR)
                else:
                    self.text.SetValue("Copy/Paste Here\nNotReady\nUnsupported data")
                    self.text.SetForegroundColour(self.BAD_COLOR)
            else:
                self.text.SetValue("Copy/Paste Here")
                self.text.SetForegroundColour(self.DEFAULT_COLOR)
        self.setting_message = False

    def auto_toggle(self, msg):
        self.auto_sync = msg.data
        if self.auto_sync:
            self.on_paste()
        self._set_message()

    def on_focus(self, event):
        self.has_focus = True
        self._set_message()

    def on_unfocus(self, event):
        self.has_focus = False
        self._set_message()

    def on_edit(self, event):
        if not self.setting_message:
            self._set_message()

    def on_copy(self, event=None):
        data = self.session.get_clipboard_data()
        data_type = self.session.get_clipboard_data_type()
        if data_type == TXT:
            text_obj = wx.TextDataObject()
            text_obj.SetText(data)

            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(text_obj)
            self.local_prev = data
            Publisher().sendMessage(("user_copy"), TXT)
            print "You copied: %s" % data
            wx.TheClipboard.Close()

            # TODO: Get this working so we don't remove clipboard data when
            #       the program exits
            # try:
            #     with wx.Clipboard.Get() as clipboard:
            #         clipboard.SetData(text_obj)
            #         clipboard.Flush()
            #         self.local_prev = data
            #         Publisher().sendMessage(("user_copy"), TXT)
            #         print "You copied: %s" % data
            # except TypeError:
            #     print "Error: Unable to write to clipboard"
        else:
            print "Nothing on clipboard"

    def on_paste(self, event=None):
        text_obj = wx.TextDataObject()
        wx.TheClipboard.Open()
        contains_text = wx.TheClipboard.GetData(text_obj)
        wx.TheClipboard.Close()
        if contains_text:
            text = text_obj.GetText()
            current = self.session.get_clipboard_data()
            current_type = self.session.get_clipboard_data_type()
            if current_type != TXT or text != current:
                print "You pasted: %s" % text
                self.session.set_clipboard_data(text, TXT)
                Publisher().sendMessage(("user_paste"), TXT)
            else:
                print "Clipboard already synced"
        else:
            print "You pasted unsupported or invalid data"

    def check_clipboard(self, event):
        if not wx.TheClipboard.IsOpened():
            text_obj = wx.TextDataObject()
            wx.TheClipboard.Open()
            contains_text = wx.TheClipboard.GetData(text_obj)
            contains_bmp = wx.TheClipboard.IsSupported(
                wx.DataFormat(wx.DF_BITMAP))
            wx.TheClipboard.Close()
            new_type = "Unkown"
            if contains_text:
                text = text_obj.GetText()
                self.has_valid_data = True
                new_type = TXT
            elif contains_bmp:
                self.has_valid_data = False
                new_type = "Bitmap"
            else:
                self.has_valid_data = False
                new_type = "Unkown"

            if new_type != self.local_prev_type:
                self.local_prev_type = new_type
                Publisher().sendMessage(("update_clipboard"), new_type)
                self._set_message()

            if self.auto_sync:
                shared = self.session.get_clipboard_data()
                shared_type = self.session.get_clipboard_data_type()
                if shared_type == TXT:
                    # If both shared clipboard and local clipboard
                    # contain different text.
                    if contains_text and shared != text:
                        # If previous local clipboard value is the same as the
                        # current local clipboard value then it was the shared
                        # clipboard that changed, so copy its value to local.
                        if self.local_prev == text: # External update
                            self.on_copy()
                        else: # This user updated
                            self.local_prev = text
                            self.on_paste()
                    # Local doesn't contain text but shared does so update local
                    elif not contains_text:
                        self.on_copy()
                # Handles the case that there is no data on shared clipboard
                # and nothing in the local clipboard and then the user copies
                # something after enbaling auto sync.
                elif contains_text:
                    self.local_prev = text
                    self.on_paste()
                        
                        
