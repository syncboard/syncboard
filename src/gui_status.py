
import wx
from wx.lib.pubsub import Publisher

class StatusPanel(wx.Panel):
    """This Panel is for managing options"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        title_font = wx.Font(pointSize=10,
                             family=wx.FONTFAMILY_DEFAULT,
                             style=wx.FONTSTYLE_NORMAL,
                             weight=wx.FONTWEIGHT_BOLD)

        sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label="Status")
        title.SetFont(title_font)
        flags = wx.SizerFlags().Proportion(0)
        title_sizer.AddF(title, flags)

        self.new = wx.StaticText(self, label="NEW")
        self.new.SetFont(title_font)
        self.new.SetForegroundColour("green")
        self.new.Hide()
        flags = wx.SizerFlags().Proportion(1).Border(wx.LEFT, 10)
        title_sizer.AddF(self.new, flags)

        flags = wx.SizerFlags().Proportion(0).Border(wx.LEFT, 20)
        sizer.AddF(title_sizer, flags)
        
        self.SetSizerAndFit(sizer)

    def update_new(self, msg):
        state = msg.data
        if msg.data:
            self.new.Show()
        else:
            self.new.Hide()
        self.GetSizer().Layout()
