#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

from spot_motion_monitor.controller.camera_controller import CameraController
from spot_motion_monitor.views.camera_control_widget import CameraControlWidget

class TestCameraController():

    def test_parametersAfterConstruction(self, qtbot):
        ccWidget = CameraControlWidget()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        assert cc.cameraControlWidget is not None
        assert cc.camera is None
        assert cc.frameTimer is not None
        assert cc.updateStatusBar is not None

    def test_cameraObject(self, qtbot):
        ccWidget = CameraControlWidget()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        assert cc.camera is not None
        assert hasattr(cc.camera, "seed")

    def test_cameraStartStop(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.startup')
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        assert cc.camera.startup.call_count == 1
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.shutdown')
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        assert cc.camera.shutdown.call_count == 1

    def test_cameraAcquireFrames(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.startStopCamera(True)
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        assert cc.frameTimer.isActive()
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        assert not cc.frameTimer.isActive()
