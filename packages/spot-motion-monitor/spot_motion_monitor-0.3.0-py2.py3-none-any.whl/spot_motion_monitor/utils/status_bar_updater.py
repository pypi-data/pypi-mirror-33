#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import QObject, pyqtSignal

__all__ = ['StatusBarUpdater']

class StatusBarUpdater(QObject):

    """Small class to allow any object to update the main application
       status bar.

    Attributes
    ----------
    displayStatus : pyqtSignal
        Signal used for updating the main application status bar.
    """

    displayStatus = pyqtSignal(str, int)
