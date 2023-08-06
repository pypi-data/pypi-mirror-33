#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.utils import FullFrameInformation, NO_DATA_VALUE
from spot_motion_monitor.views import CameraDataWidget

class TestCameraDataWidget():

    def formatFloatText(self, value):
        return "{:.2f}".format(value)

    def test_defaulTextValues(self, qtbot):
        cdw = CameraDataWidget()
        cdw.show()
        qtbot.addWidget(cdw)

        assert cdw.accumPeriodValueLabel.text() == NO_DATA_VALUE
        assert cdw.fpsValueLabel.text() == NO_DATA_VALUE
        assert cdw.numFramesAcqValueLabel.text() == NO_DATA_VALUE
        assert cdw.fluxValueLabel.text() == NO_DATA_VALUE
        assert cdw.maxAdcValueLabel.text() == NO_DATA_VALUE
        assert cdw.centroidXLabel.text() == NO_DATA_VALUE
        assert cdw.centroidYLabel.text() == NO_DATA_VALUE
        assert cdw.rmsXLabel.text() == NO_DATA_VALUE
        assert cdw.rmsYLabel.text() == NO_DATA_VALUE

    def test_PassedTextValues(self, qtbot):
        cdw = CameraDataWidget()
        cdw.show()
        qtbot.addWidget(cdw)

        ffi = FullFrameInformation(200, 342, 4032.428492, 170.482945)
        cdw.updateFullFrameData(ffi)

        assert cdw.accumPeriodValueLabel.text() == NO_DATA_VALUE
        assert cdw.fpsValueLabel.text() == NO_DATA_VALUE
        assert cdw.numFramesAcqValueLabel.text() == NO_DATA_VALUE
        assert cdw.centroidXLabel.text() == str(ffi.centerX)
        assert cdw.centroidYLabel.text() == str(ffi.centerY)
        assert cdw.fluxValueLabel.text() == self.formatFloatText(ffi.flux)
        assert cdw.maxAdcValueLabel.text() == self.formatFloatText(ffi.maxAdc)
        assert cdw.rmsXLabel.text() == NO_DATA_VALUE
        assert cdw.rmsYLabel.text() == NO_DATA_VALUE
