#/*##########################################################################
# Copyright (C) 2004-2018 V.A. Sole, European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
__author__ = "V.A. Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
import sys
import traceback

"""
This module simplifies writing code that has to deal with with PySide and PyQt4.

"""
# force cx_freeze to consider sip among the modules to add
# to the binary packages
if (('PySide.QtCore' in sys.modules) or
        (hasattr(sys, 'argv') and 'PySide' in sys.argv)):
        # argv might not be defined for embedded python (e.g., in Qt designer)
    from PySide.QtCore import *
    from PySide.QtGui import *
    try:
        from PySide.QtSvg import *
    except:
        pass
    try:
        from PySide.QtOpenGL import *
    except:
        pass
    pyqtSignal = Signal

    #matplotlib has difficulties to identify PySide
    try:
        import matplotlib
        matplotlib.rcParams['backend.qt4']='PySide'
    except:
        pass
elif "PyQt5.QtCore" in sys.modules:
    try:
        import sip
    except:
        # PyQt5 always uses API 2
        pass
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtPrintSupport import *
    try:
        from PyQt5.QtOpenGL import *
    except:
        pass
    try:
        from PyQt5.QtSvg import *
    except:
        pass
else:
    if sys.version_info < (3,):
        try:
            import sip
            sip.setapi("QString", 2)
            sip.setapi("QVariant", 2)
        except:
            print("Cannot set sip API") # Console widget not available
    try:
        from PyQt4.QtCore import *
        from PyQt4.QtGui import *
        try:
            from PyQt4.QtOpenGL import *
        except:
            pass
        try:
            from PyQt4.QtSvg import *
        except:
            pass
    except ImportError:
        try:
            # try PySide
            from PySide.QtCore import *
            from PySide.QtGui import *
            try:
                from PySide.QtSvg import *
            except:
                pass
            try:
                from PySide.QtOpenGL import *
            except:
                pass
            pyqtSignal = Signal

            # matplotlib has difficulties to identify PySide
            try:
                import matplotlib
                matplotlib.rcParams['backend.qt4']='PySide'
            except:
                pass
        except ImportError:
            from PyQt5.QtCore import *
            from PyQt5.QtGui import *
            from PyQt5.QtWidgets import *
            from PyQt5.QtPrintSupport import *
            try:
                from PyQt5.QtOpenGL import *
            except:
                pass
            try:
                from PyQt5.QtSvg import *
            except:
                pass

# provide a exception handler but not implement it by default
def exceptionHandler(type_, value, trace):
    print("%s %s %s" % (type_, value, ''.join(traceback.format_tb(trace))))
    msg = QMessageBox()
    msg.setWindowTitle("Unhandled exception")
    msg.setIcon(QMessageBox.Critical)
    msg.setInformativeText("%s %s\nPlease report details" % (type_, value))
    msg.setDetailedText(("%s " % value) + ''.join(traceback.format_tb(trace)))
    msg.raise_()
    msg.exec_()

# Overwrite the QFileDialog to make sure that by default it 
# returns non-native dialogs as it was the traditional behavior of Qt
_QFileDialog = QFileDialog
class QFileDialog(_QFileDialog):
    def __init__(self, *args, **kwargs):
        try:
            _QFileDialog.__init__(self, *args, **kwargs)
        except:
            # not all versions support kwargs
            _QFileDialog.__init__(self, *args)
        try:
            self.setOptions(_QFileDialog.DontUseNativeDialog)
        except:
            print("WARNING: Cannot force default QFileDialog behavior")

class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Fixed))

class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Expanding))
_QToolButton = QToolButton
class QToolButton(_QToolButton):
    def __init__(self, *var, **kw):
        _QToolButton.__init__(self, *var, **kw)
        if "silx" in sys.modules:
            try:
                # this should be set via a user accessible parameter
                tb = QToolBar()
                size = tb.iconSize()
                if (size.width() > 15) and (size.height() > 15):
                    self.setIconSize(size)
            except:
                print("unable")
                pass

if sys.version_info < (3,):
    import types
    # perhaps a better name would be safe unicode?
    # should this method be a more generic tool to
    # be found outside PyMcaQt?
    def safe_str(potentialQString):
        if type(potentialQString) == types.StringType or\
           type(potentialQString) == types.UnicodeType:
            return potentialQString
        try:
            # default, just str
            x = str(potentialQString)
        except UnicodeEncodeError:

            # try user OS file system encoding
            # expected to be 'mbcs' under windows
            # and 'utf-8' under MacOS X
            try:
                x = unicode(potentialQString, sys.getfilesystemencoding())
                return x
            except:
                # on any error just keep going
                pass
            # reasonable tries are 'utf-8' and 'latin-1'
            # should I really go beyond those?
            # In fact, 'utf-8' is the default file encoding for python 3
            encodingOptions = ['utf-8', 'latin-1', 'utf-16', 'utf-32']
            for encodingOption in encodingOptions:
                try:
                    x = unicode(potentialQString, encodingOption)
                    break
                except UnicodeDecodeError:
                    if encodingOption == encodingOptions[-1]:
                        raise
        return x
else:
    safe_str = str
