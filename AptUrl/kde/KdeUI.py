# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebView
from PyQt4 import uic
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *

import os
import apt_pkg
import subprocess

from AptUrl.UI import AbstractUI
from AptUrl.Helpers import _

APTURL_UI_FILE = os.environ.get(
    # Set this envar to use a test .ui file.
    'APTURL_UI_FILE',
    # System file to use if the envar is not set.
    '/usr/share/apturl/apturl-qt.ui'
    )


class AptUrlDialog(KDialog):
    def __init__(self,parent=None):
        KDialog.__init__(self,parent)
        self.setWindowIcon(KIcon("application-x-deb"))

    def slotButtonClicked(self,button):
        if button in (KDialog.Apply, KDialog.Ok, KDialog.Yes):
            KDialog.accept(self)
        else:
            KDialog.reject(self)


class KdeUI(AbstractUI):
    def __init__(self):
        self.dialog = AptUrlDialog()

        self.d = QWidget(self.dialog)
        self.dialog.setMainWidget(self.d)

        uic.loadUi(APTURL_UI_FILE, self.d)
        self.d.image_label.setPixmap(KIcon("application-x-deb").pixmap(64,64))

    # generic dialogs
    def _get_dialog(self, dialog_type, summary, msg="", buttons=KDialog.Close):
        self.dialog.setButtons(KDialog.ButtonCode(buttons))
        self.d.header_label.setText("<h2>" + summary + "</h2>")
        self.d.body_label.setText(msg)
        # TODO: title = empty
        # TODO: keep above maintain across events
        # TODO: d.set_markup("<big><b>%s</b></big>\n\n%s" % (summary, msg))

    def error(self, summary, msg=""):
        if msg != "":
            KMessageBox.detailedError(AptUrlDialog(), summary, msg)
        else:
            KMessageBox.error(AptUrlDialog(), summary)
        return False

    def message(self, summary, msg="", title=""):
        if msg != "":
            summary += "\n\n" + msg
        KMessageBox.information(AptUrlDialog(), summary, title)
        return True

    def yesNoQuestion(self, summary, msg, title="", default='no'):
        self._get_dialog('', summary, msg,
                             buttons=KDialog.Yes | KDialog.No)
        self.d.setWindowTitle(title)
        res = self.dialog.exec_()
        if res != KDialog.Accepted:
            return False
        return True

    # specific dialogs
    def askEnableChannel(self, channel, channel_info_html):
        summary = "<h2>" + _("Enable additional software channel") + "</h2>"
        msg = _("Do you want to enable the following "
                "software channel: '%s'?") % channel
        self._get_dialog('', summary, msg,
                             buttons=KDialog.Yes | KDialog.No)
        webview = QWebView()
        webview.setHtml(channel_info_html)
        webview.setFixedSize(400,200)
        self.d.vlayout_right.addWidget(webview)
        res = self.dialog.exec_()
        if res != KDialog.Accepted:
            return False
        return True

    def doEnableSection(self, sections):
        cmd = ["kdesudo",
               "--",
               "software-properties-kde",
               "--enable-component", "%s" % ' '.join(sections)]
        try:
            output = subprocess.check_output(
                cmd,
                stdout=subprocess.PIPE,
                universal_newlines=True)
        except (OSError, subprocess.CalledProcessError) as e:
            print("Execution failed: %s" % e, file=sys.stderr)
            return True
        # FIXME: Very ugly, but kdesudo doesn't return the correct exit states
        print(output)
        if not output.startswith("Enabled the "):
            return False
        return True


    def doEnableChannel(self, channelpath, channelkey):
        cmd = ["kdesudo",
               "--",
               "install", "--mode=644","--owner=0",channelpath,
               apt_pkg.Config.FindDir("Dir::Etc::sourceparts")]
        res = subprocess.call(cmd, universal_newlines=True)
        if res != 0:
            return False
        # install the key as well
        if os.path.exists(channelkey):
            cmd = ["kdesudo",
                   "--",
                   "apt-key", "add",channelkey]
            res = subprocess.call(cmd, universal_newlines=True)
            if res != 0:
                return False
        return True

    def askInstallPackage(self, package, summary, description, homepage):
        header = "<h2>" + _("Install additional software?") + "</h2>"
        body = _("Do you want to install package '%s'?") % package
        self.d.header_label.setText(header)
        self.d.body_label.setText(body)

        self.dialog.setButtons(KDialog.ButtonCode(KDialog.Yes | KDialog.No))

        res = self.dialog.exec_()
        if res != KDialog.Accepted:
            return False
        return True

    # progress etc
    def doUpdate(self):
        subprocess.check_call([
            'qapt-batch',
            '--attach', str(self.dialog.winId()),
            '--update'
            ],
            universal_newlines=True)

    def doInstall(self, apturl):
        subprocess.check_call([
            'qapt-batch',
            '--attach', str(self.dialog.winId()),
            '--install',
            apturl.package
            ],
            universal_newlines=True)


if __name__ == "__main__":
    ui = KdeUI()
    ui.error("foo","bar")

# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python;
