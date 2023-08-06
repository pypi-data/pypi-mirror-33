#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
_all__ = ['BaseCamera']

class BaseCamera():
    """Base API for all Camera classes

    Attributes
    ----------
    height : int
        The height in pixels of the camera CCD
    width : int
        The width in pixels of the camera CCD
    """

    height = None
    width = None
    fpsFullFrame = None

    def __init__(self):
        """Initialize the class.
        """
        pass

    def getFrame(self):
        """Return a CCD frame from the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def shutdown(self):
        """Shutdown the camera safely.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def startup(self):
        """Startup the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError
