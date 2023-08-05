# bug-triage -- bug triage and forward tool.
# Copyright (C) 2007  Gustavo R. Montesino
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# This file was imported from the bug-triage tool after reading this blog post:
# http://grmontesino.blogspot.ca/2007/07/exception-handling-on-pygtk.html
# Other solutions based on sys.excepthook may work better, see:
# http://faq.pygtk.org/index.py?req=show&file=faq20.010.htp
# both links are broken above, see instead:
# http://www.sysfs.be/downloads/gtkexcepthook.py
# https://github.com/mypaint/mypaint/blob/master/gui/gtkexcepthook.py
# the latter also has hooks to send github bug reports!

import pygtk
pygtk.require("2.0")
import gtk
import traceback

import monkeysign.ui
import monkeysign.translation

def msg_exception(exception):
    """Shows information about a exception in a gtk dialog"""

    msg = ExceptionDialog(exception)
    msg.run()
    msg.destroy()

def errorhandler(f):
    """Error handler decorator"""
    def wrapper(*args, **kargs):
        try:
            return f(*args, **kargs)
        except Exception as instance:
            if type(instance) not in [KeyboardInterrupt, SystemExit]:
                msg_exception(instance)
    return wrapper

class ExceptionDialog(gtk.MessageDialog):
    def __init__(self, instance):
        gtk.MessageDialog.__init__(self, buttons=gtk.BUTTONS_CLOSE, type=gtk.MESSAGE_ERROR)
        self.set_resizable(True)
        self.set_markup(_("An error has occured:\n%r\nYou should save "
                "your work and restart the application. If the error "
                "occurs again please report it to the developer." % str(instance)))
        self.set_title(_("Error"))
        expander = gtk.Expander(_("Exception Details"))
        self.vbox.pack_start(expander)
        textview = gtk.TextView()
        text = "\n".join(monkeysign.gtkui.MonkeysignScanUi.sysinfo()) \
               + "\n" + traceback.format_exc()
        textview.get_buffer().set_text(text)
        expander.add(self.scrolled(textview))
        self.show_all()

    def scrolled(self, widget, shadow=gtk.SHADOW_NONE):
        window = gtk.ScrolledWindow()
        window.set_shadow_type(shadow)
        window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        if widget.set_scroll_adjustments(window.get_hadjustment(),
                                          window.get_vadjustment()):
            window.add(widget)
        else:
            window.add_with_viewport(widget)
        return window

class test:
    @errorhandler
    def __init__(self):
        raise Exception("test exception")

if __name__ == '__main__':
    test()
            
# vim: tabstop=4 expandtab shiftwidth=4     
