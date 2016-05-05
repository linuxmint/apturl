import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
GObject.threads_init()

import os
import sys
import apt_pkg
import subprocess
import tempfile

from AptUrl.UI import AbstractUI
from AptUrl import Helpers
from AptUrl.Helpers import _

APTURL_UI_FILE = os.environ.get(
    # Set this envar to use a test .ui file.
    'APTURL_UI_FILE',
    # System file to use if the envar is not set.
    '/usr/share/apturl/apturl-gtk.ui'
    )


class GtkUI(AbstractUI):
    def __init__(self):
        Gtk.init_check(sys.argv)
        # create empty dialog
        self.dia_xml = Gtk.Builder()
        self.dia_xml.set_translation_domain("apturl")
        self.dia_xml.add_from_file(APTURL_UI_FILE)
        self.dia = self.dia_xml.get_object('confirmation_dialog')
        self.dia.start_available = lambda: Gtk.main_quit()
        self.dia.start_error = lambda: Gtk.main_quit()
        self.dia.exit = lambda: Gtk.main_quit()
        self.dia.realize()
        self.require_update = False

    # generic dialogs
    def _get_dialog(self, dialog_type, summary, msg="",
                    buttons=Gtk.ButtonsType.CLOSE):
        " internal helper for dialog construction "
        d = Gtk.MessageDialog(parent=self.dia,
                              flags=Gtk.DialogFlags.MODAL,
                              type=dialog_type,
                              buttons=buttons)
        d.set_title("")
        d.set_markup("<big><b>%s</b></big>\n\n%s" % (summary, msg))
        d.set_icon(Gtk.IconTheme.get_default().load_icon('package-x-generic', 16, False))
        d.set_keep_above(True)
        d.realize()
        d.get_window().set_functions(Gdk.WMFunction.MOVE)
        return d

    def error(self, summary, msg=""):
        d = self._get_dialog(Gtk.MessageType.ERROR, summary, msg)
        d.run()
        d.destroy()
        return False

    def message(self, summary, msg="", title=""):
        d = self._get_dialog(Gtk.MessageType.INFO, summary, msg)
        d.set_title(title)
        d.run()
        d.destroy()
        return True

    def yesNoQuestion(self, summary, msg, title="", default='no'):
        d = self._get_dialog(Gtk.MessageType.QUESTION, summary, msg,
                             buttons=Gtk.ButtonsType.YES_NO)
        d.set_title(title)
        res = d.run()
        d.destroy()
        if res != Gtk.ResponseType.YES:
            return False
        return True

    def askInstallPackage(self, package, summary, description, homepage):
        # populate the dialog
        dia = self.dia
        dia_xml = self.dia_xml
        header = _("Install additional software?")
        body = _("Do you want to install package '%s'?") % package
        dia.set_title('')
        header_label = dia_xml.get_object('header_label')
        header_label.set_markup("<b><big>%s</big></b>" % header)
        body_label = dia_xml.get_object('body_label')
        body_label.set_label(body)
        description_text_view = dia_xml.get_object('description_text_view')
        tbuf = Gtk.TextBuffer()
        desc = "%s\n\n%s" % (summary, Helpers.format_description(description))
        tbuf.set_text(desc)
        description_text_view.set_buffer(tbuf)
        dia.set_icon(Gtk.IconTheme.get_default().load_icon('package-x-generic', 16, False))

        # check if another package manager is already running
        # FIXME: just checking for the existance of the file is
        #        not sufficient, it need to be tested if it can
        #        be locked via apt_pkg.get_lock()
        #        - but that needs to run as root
        #        - a dbus helper might be the best answer here
        #args = (update_button_status, dia_xml.get_object("yes_button"),
        #    dia_xml.get_object("infolabel"))
        #args[0](*args[1:])
        #timer_id = GObject.timeout_add(750, *args )

        # show the dialog
        res = dia.run()
        #GObject.source_remove(timer_id)
        if res != Gtk.ResponseType.YES:
            dia.hide()
            return False

        return True

    # progress etc
    def doUpdate(self):
        self.require_update = True
        win = self.dia.get_window()
        try:
            xid = win.get_xid()
        except Exception as e:
            print(e)
            xid = 0
        FNULL = open(os.devnull, 'w')
        cmd = ["sudo", "/usr/lib/linuxmint/mintUpdate/checkAPT.py", "--use-synaptic", "%d" % xid]
        comnd = subprocess.Popen(' '.join(cmd), stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        returnCode = comnd.wait()

    def doInstall(self, apturl):
        self.dia.hide()
        win = self.dia.get_window()
        try:
            xid = win.get_xid()
        except Exception as e:
            print(e)
            xid = 0

        cmd = ["pkexec", "/usr/sbin/synaptic", "--hide-main-window",  "--non-interactive", "--parent-window-id", "%s" % xid]
        cmd.append("-o")
        cmd.append("Synaptic::closeZvt=true")
        f = tempfile.NamedTemporaryFile()
        for pkg in [apturl.package]:
            pkg_line = "%s\tinstall\n" % pkg
            f.write(pkg_line.encode("utf-8"))
        cmd.append("--set-selections-file")
        cmd.append("%s" % f.name)
        f.flush()
        comnd = subprocess.Popen(' '.join(cmd), shell=True)
        returnCode = comnd.wait()
        f.close()
        self.dia.exit()

if __name__ == "__main__":
    ui = GtkUI()
    ui.error("foo","bar")
