#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMainWindow

from spot_motion_monitor.utils import ONE_SECOND_IN_MILLISECONDS
from spot_motion_monitor.views.main_window import SpotMotionMonitor

class TestMainWindow():

    # def setup_class(cls):
    #     cls.fastTimeout = 1250  # ms

    def test_mainWindowExit(self, qtbot, mocker):
        mocker.patch('PyQt5.QtWidgets.QMainWindow.close')
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        mw.actionExit.trigger()
        assert QMainWindow.close.call_count == 1

    def test_mainWindowAbout(self, qtbot, mocker):
        mocker.patch('spot_motion_monitor.views.main_window.SpotMotionMonitor.about')
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        mw.actionAbout.trigger()
        assert SpotMotionMonitor.about.call_count == 1

    def test_setActionIcon(self, qtbot):
        mw = SpotMotionMonitor()
        qtbot.addWidget(mw)
        action = QAction()
        mw.setActionIcon(action, "test.png", True)
        assert action.icon() is not None
        assert action.isIconVisibleInMenu() is True

    def test_updateStatusBar(self, qtbot):
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        message1 = "Hello World!"
        mw.cameraController.updateStatusBar.displayStatus.emit(message1, ONE_SECOND_IN_MILLISECONDS)
        assert mw.statusbar.currentMessage() == message1
        message2 = "Have a nice evening!"
        mw.plotController.updateStatusBar.displayStatus.emit(message2, ONE_SECOND_IN_MILLISECONDS)
        assert mw.statusbar.currentMessage() == message2

    # def test_acquire_frame(self, qtbot, mocker):
    #     mw = SpotMotionMonitor()
    #     qtbot.addWidget(mw)
    #     mocker.patch('spot_motion_monitor.views.main_window.SpotMotionMonitor.acquireFrame')
    #     signals = [mw.cameraController.cc_widget.acquireFramesState,
    #                mw.cameraController.frameTimer.timeout]
    #     with qtbot.waitSignals(signals):  # , timeout=self.fastTimeout):
    #         qtbot.mouseClick(mw.cameraControl.acquireFramesButton, Qt.LeftButton)
    #     assert mw.acquireFrame.call_count == 1
    #     qtbot.mouseClick(mw.cameraControl.acquireFramesButton, Qt.LeftButton)
