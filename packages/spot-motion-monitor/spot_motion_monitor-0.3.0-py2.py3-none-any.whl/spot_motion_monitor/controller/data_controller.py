#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.models import FullFrameModel
from spot_motion_monitor.utils import FrameRejected, FullFrameInformation
from spot_motion_monitor.utils import STATUSBAR_FAST_TIMEOUT, StatusBarUpdater

__all__ = ["DataController"]

class DataController():

    """This class manages the interactions between the information calculated
       by a particular frame model and the CameraDataWidget.

    Attributes
    ----------
    cameraDataWidget : .CameraDataWidget
        An instance of the camera data widget.
    fullFrameModel : .FullFrameModel
        An instance of the full frame calculation model.
    updateStatusBar : .StatusBarUpdater
        An instance of the status bar updater.
    """

    def __init__(self, cdw):
        """Initialize the class.

        Parameters
        ----------
        cdw : .CameraDataWidget
            An instance of the camera data widget.
        """
        self.cameraDataWidget = cdw
        self.fullFrameModel = FullFrameModel()
        self.updateStatusBar = StatusBarUpdater()

    def passFrame(self, frame):
        """Get a frame, do calculations and update information.

        Parameters
        ----------
        frame : numpy.array
            A frame from a camera CCD.
        """
        try:
            genericFrameInfo = self.fullFrameModel.calculateCentroid(frame)
            fullFrameInfo = FullFrameInformation(int(genericFrameInfo.centerX), int(genericFrameInfo.centerY),
                                                 genericFrameInfo.flux, genericFrameInfo.maxAdc)
            self.cameraDataWidget.updateFullFrameData(fullFrameInfo)
        except FrameRejected as err:
            self.updateStatusBar.displayStatus.emit(str(err), STATUSBAR_FAST_TIMEOUT)
