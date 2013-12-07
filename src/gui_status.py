
import wx
from wx.lib.pubsub import Publisher

class StatusPanel(wx.Panel):
    """This Panel is for managing options"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        t = wx.StaticText(self, label="Status")
        sizer.Add(t)
        self.SetSizerAndFit(sizer)
