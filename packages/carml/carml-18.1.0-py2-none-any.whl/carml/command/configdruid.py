from __future__ import print_function

import os
import sys
import functools

import zope.interface
from twisted.python import usage, log
from twisted.protocols.basic import LineReceiver
from twisted.internet import defer, stdio

from PyQt4 import QtGui

import txtorcon
from carml.interface import ICarmlCommand
from carml import util


class ConfigDruidOptions(usage.Options):
    def __init__(self):
        super(ConfigDruidOptions, self).__init__()
        self.longOpt.remove('version')
        self.longOpt.remove('help')
        self.args = None


def do_cmd(proto, args):
    def _print(res):
        print(res)

    def _error(arg):
        print(util.colors.red(arg.getErrorMessage()))
        return None
    d = defer.Deferred()
    # launch qt gui? in own thread, or what? how do we integrate here?
    # Create a Qt application

    app = QtGui.QApplication(sys.argv)
    # Create a Label and show it
    label = QtGui.QLabel("Hello World")
    label.show()
    # Enter Qt application main loop
#    app.exec_()
#    sys.exit()

    return d


# see cmd_info for an alternate way to implement this via a method
# with attributes and "zope.interface.implementsDirectly()"
# trying out both ways to see what feels better
@zope.interface.implementer(ICarmlCommand)
class ConfigDruidCommand(object):
    # Attributes specified by ICarmlCommand
    name = 'configdruid'
    help_text = 'Launch a Qt-based interactive configuration druid.'
    controller_connection = True
    build_state = False
    options_class = ConfigDruidOptions

    def validate(self, options, mainoptions):
        pass

    @defer.inlineCallbacks
    def run(self, options, mainoptions, proto):
        """
        ICarmlCommand API
        """

        yield do_cmd(proto, options.args)

cmd = ConfigDruidCommand()
__all__ = ['cmd']
