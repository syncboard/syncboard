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
    This contails gui elements responsible for displaying application info.
"""

import wx, wx.html, wx.lib.wxpTag, webbrowser
import info

LICENSE_SIZE = (500, 500)
ABOUT_SIZE = (300, 300)

class LicenseDialog(wx.Dialog):
    """Displays the full license in a scolling window."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "License")
        
        ok_btn = wx.Button(self, wx.ID_OK, "OK")
        
        text = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=LICENSE_SIZE)
        text.SetEditable(False)
        text.SetValue(info.LICENSE_TEXT)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text,
                  proportion=0,
                  flag=wx.EXPAND | wx.ALL,
                  border=5)
        sizer.Add(ok_btn,
                  proportion=0,
                  flag= wx.ALIGN_CENTER | wx.ALL,
                  border=5)
        
        self.SetSizerAndFit(sizer)
        self.Center(wx.BOTH)


ABOUT_TEXT = """
<html>
<body bgcolor="#F0F0F0">
<center><table bgcolor="#F0F0F0" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    <h1>%s %s</h1>
    </td>
</tr>
</table>

<p><b>%s</b> is %s brought to you by %s
Copyright %s.</p>

<p><a href=%s>%s</a></p>

<p><wxp module="wx" class="Button">
    <param name="label" value="License">
</wxp></p>

<p><wxp module="wx" class="Button">
    <param name="label" value="Close">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
"""

class wxHTML(wx.html.HtmlWindow):
    """Subclassed so we can open links in the user's browser."""
    def OnLinkClicked(self, link):
        webbrowser.open(link.GetHref())

class AboutDialog(wx.Dialog):
    """Displays app info in a new dialog window."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "About " + info.NAME,
                           size=ABOUT_SIZE)

        html = wxHTML(self, wx.ID_ANY, size=(420, -1))
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        # Produces "dev1, dev2, ..., and dev3" where each name is bolded
        devs = ("<b>" + "</b>, <b>".join(info.DEVELOPERS[0:-1]) +
                "</b> and <b>" + info.DEVELOPERS[-1] + "</b>")
        txt = ABOUT_TEXT % (info.NAME, info.VERSION, info.NAME,
                            info.DESCRIPTION_TEXT, devs, info.COPYRIGHT,
                            info.WEBSITE[0], info.WEBSITE[1])
        html.SetPage(txt)
        
        license_btn = html.FindWindowByLabel("License")
        license_btn.Bind(wx.EVT_BUTTON, self.on_license)
        
        ok_btn = html.FindWindowById(wx.ID_OK)

        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        
        self.Center(wx.BOTH)

    def on_license(self, event):
        licensebox = LicenseDialog(self)
        licensebox.ShowModal()
        licensebox.Destroy()
