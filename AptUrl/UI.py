
from .Helpers import _, _n

class AbstractUI(object):
    # generic dialogs
    def error(self, summary, msg):
        return False
    def yesNoQuestion(self, summary, msg, title, default='no'):
        pass
    def message(self, summary, msg):
        return True

    def askInstallPackage(self):
        pass

    # install/update progress 
    def doUpdate(self):
        pass
    def doInstall(self, apturl, extra_pkg_names=None):
        pass

    # UI specific actions for enabling stuff

