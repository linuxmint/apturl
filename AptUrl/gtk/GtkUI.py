import gi
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import XApp
GObject.threads_init()

import os
import sys
import apt_pkg
import subprocess
import tempfile

from AptUrl.UI import AbstractUI
from AptUrl import Helpers
from AptUrl.Helpers import _

import mintcommon.aptdaemon

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
        XApp.set_window_icon_name(d, "package-x-generic")
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
        dia.set_title(package)
        header_label = dia_xml.get_object('header_label')
        header_label.set_markup("<b><big>%s</big></b>" % header)
        body_label = dia_xml.get_object('body_label')
        body_label.set_label(body)
        description_text_view = dia_xml.get_object('description_text_view')
        tbuf = Gtk.TextBuffer()
        desc = "%s\n\n%s" % (summary, Helpers.format_description(description))
        tbuf.set_text(desc)
        description_text_view.set_buffer(tbuf)
        XApp.set_window_icon_name(dia, "package-x-generic")

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

    def doInstall(self, apturl):
        self.dia.hide()
        packages = []
        packages.append(apturl.package)
        self.install_packages(packages)

    def install_packages(self, package_names):
        self.apt = mintcommon.aptdaemon.APT(None)
        self.package_names = package_names
        self.busy = True
        if self.require_update:
            self.apt.set_finished_callback(self.on_update_before_install_finished)
            self.apt.update_cache()
        else:
            self.on_update_before_install_finished()
        while self.busy:
            while Gtk.events_pending():
                Gtk.main_iteration()

    def on_update_before_install_finished(self, transaction=None, exit_state=None):
        self.apt.set_finished_callback(self.on_install_finished)
        self.apt.set_cancelled_callback(self.on_install_finished)
        self.apt.install_packages(self.package_names)

    def on_install_finished(self, transaction=None, exit_state=None):
        del self.package_names
        del self.apt
        self.busy = False
        self.dia.exit()

if __name__ == "__main__":
    ui = GtkUI()
    ui.error("foo","bar")
