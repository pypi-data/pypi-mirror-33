#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.camera.gaussian_camera import GaussianCamera

class TestGaussianCamera():

    def setup_class(self):
        self.camera = GaussianCamera()

    def test_parametersAfterConstruction(self):
        assert self.camera.height is None
        assert self.camera.width is None
        assert self.camera.seed is None
        assert self.camera.fpsFullFrame is None

    def test_parametersAfterStartup(self):
        self.camera.startup()
        assert self.camera.height == 480
        assert self.camera.width == 640
        assert self.camera.fpsFullFrame == 24

    def test_getFrame(self):
        self.camera.seed = 1000
        self.camera.startup()
        frame = self.camera.getFrame()
        assert frame.shape == (480, 640)
        max_point1, max_point2 = np.where(frame == np.max(frame))
        assert max_point1[0] == 225
        assert max_point2[0] == 288
