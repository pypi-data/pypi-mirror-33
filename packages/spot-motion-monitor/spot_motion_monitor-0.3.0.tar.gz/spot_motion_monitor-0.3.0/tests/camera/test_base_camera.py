#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import pytest

from spot_motion_monitor.camera.base_camera import BaseCamera

class TestBaseCamera(object):

    def setup_class(self):
        self.baseCamera = BaseCamera()

    def test_nullParametersAfterConstruction(self):
        assert self.baseCamera.height is None
        assert self.baseCamera.width is None
        assert self.baseCamera.fpsFullFrame is None

    def test_noApiAfterConstruction(self):
        with pytest.raises(NotImplementedError):
            self.baseCamera.startup()

        with pytest.raises(NotImplementedError):
            self.baseCamera.shutdown()

        with pytest.raises(NotImplementedError):
            self.baseCamera.getFrame()
