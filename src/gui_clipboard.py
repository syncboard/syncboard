
import wx
from wx.lib.pubsub import Publisher

class ClipboardPanel(wx.Panel):
    """
    This Panel is where the user copies and pastes. (it will also be for
    displaying clipboard contents if we choose to do so)
    """
    OK_COLOR = (0, 200, 0)
    BAD_COLOR = (255, 100, 0)
    UNKNOWN_COLOR = (200, 0, 0)
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.message = ""

        self.text = wx.TextCtrl(self, size=(150, 50),
                        style=wx.TE_CENTER | wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        
        sizer.Add(self.text)

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_IDLE, self.check_clipboard)
        self.Bind(wx.EVT_TEXT_COPY, self.on_copy)
        self.Bind(wx.EVT_TEXT_PASTE, self.on_paste)
        self.Bind(wx.EVT_TEXT, self.reset)

        self.prev_clipboard_content = ""
        self.dont_reset = False

        self.reset()

        Publisher().subscribe(self.auto_toggle, "auto_toggle")

        self.i = 0

    def auto_toggle(self, msg):
        m = "TODO: implement auto sync"
        if msg:
            print "auto sync on - %s" % m
        else:
            print "auto sync off - %s" % m

    def on_copy(self, event):
        self.i += 1
        data = "You've copied %d times - TODO: Get data from backend" % self.i
        
        clipdata = wx.TextDataObject()
        clipdata.SetText(data)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        print "Youre clipboard:", data

    def on_paste(self, event):
        do = wx.TextDataObject()
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(do)
        wx.TheClipboard.Close()
        if success:
            text = do.GetText()
            if text != self.prev_clipboard_content:
                print "You pasted: %s - TODO: Send data to backend" % text
                self.prev_clipboard_content = text
        else:
            print "You pasted unsupported invalid data"


    def reset(self, event=None):
        if self.dont_reset:
            self.dont_reset = False
        else:
            self.dont_reset = True
            self.text.SetValue(self.message)

    def check_clipboard(self, event):
        m = "Copy/Paste Here"
        if not wx.TheClipboard.IsOpened():
            wx.TheClipboard.Open()
            contains_text = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT))
            contains_bmp = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP))
            wx.TheClipboard.Close()
            if contains_text:
                self.message = m + "\nYour Clipboard Data:\nTEXT"
                self.text.SetForegroundColour(self.OK_COLOR)
            elif contains_bmp:
                self.message = "Don't " + m + "\nYour Clipboard Data:\nBITMAP (unsupported)"
                self.text.SetForegroundColour(self.BAD_COLOR)
            else:
                self.message = "Don't " + m + "\nYour Clipboard Data:\nUNKNOWN"
                self.text.SetForegroundColour(self.UNKNOWN_COLOR)
            self.reset()
