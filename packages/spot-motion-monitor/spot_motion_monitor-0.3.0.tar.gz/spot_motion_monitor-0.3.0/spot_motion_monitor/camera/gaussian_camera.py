#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.camera import BaseCamera

__all__ = ['GaussianCamera']

class GaussianCamera(BaseCamera):

    """This class creates a camera that produces a frame with random Poisson
       noise and a Gaussian spot placed at random within the frame.

    Attributes
    ----------
    height : int
        The pixel height of the CCD.
    postageStamp : numpy.array
        The array containing the Gaussian postage stamp.
    seed : int
        The seed for the random number generator.
    width : int
        The pixel width of the CCD.
    xPoint : int
        The x-coordinate of the Gaussian postage stamp insertion point.
    yPoint : int
        The y-coordinate of the Gaussian postage stamp insertion point.
    """

    seed = None

    def __init__(self):
        """Initalize the class.
        """
        super().__init__()

    def findInsertionPoint(self):
        """Determine the Gaussian spot insertion point.
        """
        percentage = 0.2
        xRange = percentage * self.width
        yRange = percentage * self.height
        # Pick lower left corner for insertion
        xHalfwidth = self.width / 2
        yHalfwidth = self.height / 2
        self.xPoint = np.random.randint(xHalfwidth - xRange, xHalfwidth + xRange + 1)
        self.yPoint = np.random.randint(yHalfwidth - yRange, yHalfwidth + yRange + 1)

    def getFrame(self):
        """Get the frame from the CCD.

        Returns
        -------
        numpy.array
            The current CCD frame.
        """
        # Create base CCD frame
        ccd = np.random.poisson(20.0, (self.height, self.width))

        # Merge CCD frame and postage stamp
        ccd[self.yPoint:self.yPoint + self.postageStamp.shape[0],
            self.xPoint:self.xPoint + self.postageStamp.shape[1]] += self.postageStamp

        return ccd

    def makePostageStamp(self):
        """Create the Gaussian spot.
        """
        x, y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))
        d = np.sqrt(x * x + y * y)
        sigma, mu = 0.5, 0.0
        a = 200.0 / (sigma * np.sqrt(2.0 * np.pi))
        self.postageStamp = a * np.exp(-((d - mu)**2 / (2.0 * sigma**2)))
        self.postageStamp = self.postageStamp.astype(np.int64)

    def startup(self):
        """Handle the startup of the camera.
        """
        self.height = 480
        self.width = 640
        self.fpsFullFrame = 24
        np.random.seed(self.seed)
        self.makePostageStamp()
        self.findInsertionPoint()

    def shutdown(self):
        """Handle the shutdown of the camera.
        """
        pass
