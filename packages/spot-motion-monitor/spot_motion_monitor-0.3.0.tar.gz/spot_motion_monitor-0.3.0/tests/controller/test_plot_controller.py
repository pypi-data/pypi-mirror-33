#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
#from pyqtgraph import ImageView, PlotItem

from spot_motion_monitor.controller.plot_controller import PlotController
from spot_motion_monitor.views.camera_plot_widget import CameraPlotWidget

class TestPlotController():

    def test_parametersAfterConstruction(self, qtbot):
        cpw = CameraPlotWidget()
        qtbot.addWidget(cpw)
        pc = PlotController(cpw)
        assert pc.cameraPlotWidget is not None
        assert pc.updateStatusBar is not None

    def test_passFrame(self, qtbot):
        cpw = CameraPlotWidget()
        cpw.show()
        qtbot.addWidget(cpw)
        pc = PlotController(cpw)
        frame = np.ones((3, 5))
        pc.passFrame(frame)
        pc.cameraPlotWidget.image.shape = (3, 5)
