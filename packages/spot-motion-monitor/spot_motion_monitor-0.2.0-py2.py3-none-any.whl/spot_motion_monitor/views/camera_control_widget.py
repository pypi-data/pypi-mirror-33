#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from spot_motion_monitor.views.ui_camera_control import Ui_CameraControl

__all__ = ['CameraControlWidget']

class CameraControlWidget(QWidget, Ui_CameraControl):

    """This class handles the interactions from the Camera Control Widget on
    the Main Window.

    Attributes
    ----------
    acquireFramesState : pyqtSignal
        Signal the state of acquiring frames.
    acquireRoiState : pyqtSignal
        Signal the state of acquiring in ROI mode.
    cameraState : pyqtSignal
        Signal state of camera.
    """

    acquireFramesState = pyqtSignal(bool)
    acquireRoiState = pyqtSignal(bool)
    cameraState = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialze the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.setupUi(self)

        self.startStopButton.toggled.connect(self.handleStartStop)
        self.acquireFramesButton.toggled.connect(self.handleAcquireFrames)
        self.acquireRoiCheckBox.toggled.connect(self.handleAcquireRoi)

    def handleAcquireFrames(self, checked):
        """Perform actions related to acquiring frames.

        Parameters
        ----------
        checked : bool
            State of the toggle button.
        """
        if checked:
            self.acquireFramesButton.setText("Stop Acquire Frames")
        else:
            self.acquireFramesButton.setText("Start Acquire Frames")
        self.acquireFramesState.emit(checked)

    def handleAcquireRoi(self, checked):
        """Perform actions related to acquiring in ROI mode.

        Parameters
        ----------
        checked : bool
            State of the checkbox.
        """
        self.acquireRoiState.emit(checked)

    def handleStartStop(self, checked):
        """Perform actions related to startup/shutdown of the camera.

        Parameters
        ----------
        checked : bool
            State of the toggle button.
        """
        if checked:
            self.startStopButton.setText("Stop Camera")
        else:
            self.startStopButton.setText("Start Camera")
        self.cameraState.emit(checked)
