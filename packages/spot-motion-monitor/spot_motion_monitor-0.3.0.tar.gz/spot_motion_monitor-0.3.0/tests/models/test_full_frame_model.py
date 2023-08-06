#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
import pytest

from spot_motion_monitor.camera.gaussian_camera import GaussianCamera
from spot_motion_monitor.models import FullFrameModel
from spot_motion_monitor.utils import FrameRejected

class TestFullFrameModel():

    def setup_class(cls):
        cls.model = FullFrameModel()

    def test_parametersAfterConstruction(self):
        assert self.model.sigmaScale == 5.0
        assert self.model.minimumNumPixels == 10

    def test_frameCalculations(self):
        # This test requires the generation of a CCD frame which will be
        # provided by the GaussianCamera
        camera = GaussianCamera()
        camera.seed = 1000
        camera.startup()
        frame = camera.getFrame()
        info = self.model.calculateCentroid(frame)
        assert info.centerX == 288.45394404821826
        assert info.centerY == 224.47687644439395
        assert info.flux == 3235.9182163661176
        assert info.maxAdc == 135.83703259361937
        assert info.stdNoObjects is None

    def test_badFrameCalculation(self):
        frame = np.ones((480, 640))
        with pytest.raises(FrameRejected):
            self.model.calculateCentroid(frame)
