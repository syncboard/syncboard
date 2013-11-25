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
This file contains information about the application itself and the wxPython
elements for displaying it.
"""

from os.path import join

f = open(join(".." + "/" + "LICENSE"), "r")
msg = f.read()
f.close()

LICENSE_TEXT = msg
DESCRIPTION_TEXT = "a cross-platform clipboard syncing tool"
      
NAME = "Syncboard"
VERSION = "0.0.0"
COPYRIGHT = "(C) 2013"
WEBSITE = ("https://github.com/syncboard/syncboard", "Source on Github")
DEVELOPERS = [ "Brandon Edgren", "Nat Mote"]

import wx

class LicenseDialog(wx.Dialog):
    """Displays the full license in a scolling window."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "License")
        
        ok_btn = wx.Button(self, wx.ID_OK, "OK")
        
        text = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(500, 500))
        text.SetEditable(False)
        text.SetValue(LICENSE_TEXT)

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
        self.CentreOnParent(wx.BOTH)


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

import wx.html, wx.lib.wxpTag, webbrowser

class wxHTML(wx.html.HtmlWindow):
    """Subclassed so we can open links in the user's browser."""
    def OnLinkClicked(self, link):
        webbrowser.open(link.GetHref())

class AboutDialog(wx.Dialog):
    """Displays app info in a new dialog window."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "About " + NAME, size=(300, 300))

        html = wxHTML(self, wx.ID_ANY, size=(420, -1))
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        # Produces "dev1, dev2, ..., and dev3" where each name is bolded
        devs = ("<b>" + "</b>, <b>".join(DEVELOPERS[0:-1]) + "</b> and <b>" +
                DEVELOPERS[-1] + "</b>")
        txt = ABOUT_TEXT % (NAME, VERSION, NAME, DESCRIPTION_TEXT, devs,
                            COPYRIGHT, WEBSITE[0], WEBSITE[1])
        html.SetPage(txt)
        
        license_btn = html.FindWindowByLabel("License")
        license_btn.Bind(wx.EVT_BUTTON, self.on_license)
        
        ok_btn = html.FindWindowById(wx.ID_OK)

        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        
        self.CentreOnParent(wx.BOTH)

    def on_license(self, event):
        licensebox = LicenseDialog(self)
        licensebox.ShowModal()
        licensebox.Destroy()
