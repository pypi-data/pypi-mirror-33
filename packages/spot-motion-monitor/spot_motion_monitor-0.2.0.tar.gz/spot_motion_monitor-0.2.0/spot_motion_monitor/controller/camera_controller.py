#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import QTimer

import spot_motion_monitor.camera
import spot_motion_monitor.utils as smmUtils

__all__ = ["CameraController"]

class CameraController():

    """This class manages the interactions between the CameraControlWidget and
       a particular instance of a BaseCamera.

    Attributes
    ----------
    camera : .BaseCamera
        A particular concrete instance of a camera.
    cameraControlWidget : .CameraControlWidget
        The instance of the camera control widget.
    """

    def __init__(self, ccw):
        """Initialize the class.

        Parameters
        ----------
        ccw : .CameraControlWidget
            An instance of the camera control widget
        """
        self.cameraControlWidget = ccw
        self.camera = None
        self.updateStatusBar = smmUtils.StatusBarUpdater()
        self.frameTimer = QTimer()

        self.cameraControlWidget.cameraState.connect(self.startStopCamera)
        self.cameraControlWidget.acquireFramesState.connect(self.acquireFrame)

    def acquireFrame(self, state):
        if state:
            self.updateStatusBar.displayStatus.emit('Starting Frame Acquisition',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
            if self.frameTimer.isActive():
                self.frameTimer.stop()
            fps = self.camera.fpsFullFrame if self.camera.fpsFullFrame is not None else smmUtils.DEFAULT_FPS
            self.frameTimer.start(smmUtils.ONE_SECOND_IN_MILLISECONDS / fps)
        else:
            self.updateStatusBar.displayStatus.emit('Stopping Frame Acquistion',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.frameTimer.stop()

    def setupCamera(self, cameraStr):
        """Create a specific concrete instance of a camera.

        Parameters
        ----------
        cameraStr : str
            Class name for concrete camera instance.
        """
        self.camera = getattr(spot_motion_monitor.camera, cameraStr)()

    def startStopCamera(self, state):
        """Summary

        Parameters
        ----------
        state : bool
            The current state of the camera.
        """
        if state:
            self.updateStatusBar.displayStatus.emit('Starting Camera',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.camera.startup()
            self.updateStatusBar.displayStatus.emit('Camera Started Successfully',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
        else:
            self.updateStatusBar.displayStatus.emit('Stopping Camera',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.camera.shutdown()
            self.updateStatusBar.displayStatus.emit('Camera Stopped Successfully',
                                                    smmUtils.ONE_SECOND_IN_MILLISECONDS)
