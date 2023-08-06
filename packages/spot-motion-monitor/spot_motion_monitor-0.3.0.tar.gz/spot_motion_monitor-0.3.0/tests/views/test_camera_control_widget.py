#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

from spot_motion_monitor.views.camera_control_widget import CameraControlWidget

class TestCameraControl():

    def setup_class(self):
        self.fast_timeout = 250  # ms

    def stateIsFalse(self, state):
        return not state

    def stateIsTrue(self, state):
        return state

    def test_startStopCameraButton(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert not cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Start Camera"
        with qtbot.waitSignal(cc.cameraState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Stop Camera"
        with qtbot.waitSignal(cc.cameraState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert not cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Start Camera"

    def test_acquireFramesButton(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert not cc.acquireFramesButton.isChecked()
        assert cc.acquireFramesButton.text() == "Start Acquire Frames"
        with qtbot.waitSignal(cc.acquireFramesState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.acquireFramesButton, Qt.LeftButton)
        assert cc.acquireFramesButton.isChecked()
        assert cc.acquireFramesButton.text() == "Stop Acquire Frames"
        with qtbot.waitSignal(cc.acquireFramesState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.acquireFramesButton, Qt.LeftButton)
        assert not cc.acquireFramesButton.isChecked()
        assert cc.acquireFramesButton.text() == "Start Acquire Frames"

    def test_acquireRoiCheckbox(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert not cc.acquireRoiCheckBox.isChecked()
        with qtbot.waitSignal(cc.acquireRoiState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.acquireRoiCheckBox, Qt.LeftButton)
        assert cc.acquireRoiCheckBox.isChecked()
        with qtbot.waitSignal(cc.acquireRoiState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.acquireRoiCheckBox, Qt.LeftButton)
        assert not cc.acquireRoiCheckBox.isChecked()
