# -*- coding: utf-8 -*-
"""
This module implement classes that can be used in stytra to control cameras.
"""
import numpy as np

try:
    from ximea import xiapi
except ImportError:
    pass
try:
    from pymba import Vimba
    from pymba.vimbaexception import VimbaException
except ImportError:
    pass


class Camera:
    """Abstract class for controlling a camera.

    Subclasses implement minimal
    control over the following cameras:
     - Ximea (uses ximea python API `xiAPI <https://www.ximea.com/support/wiki/apis/Python>`_;
     - AVT   (uses `pymba <https://github.com/morefigs/pymba>`_,
       a python wrapper for AVT Vimba package).

    Examples
    --------
    Simple usage of a camera class::

        cam = AvtCamera()
        cam.open_camera()  # initialize the camera
        cam.set('exposure', 10)  # set exposure time in ms
        frame = cam.read()  # read frame
        cam.release()  # close the camera


    Attributes
    ----------
    cam :
        camera object (class depends on camera type).

    debug : bool
        if true, state of the camera is printed.


    """

    def __init__(self, debug=False):
        """
        Parameters
        ----------
        debug : str
            if True, info about the camera state will be printed.
        """
        self.cam = None
        self.debug = debug

    def open_camera(self):
        """Initialise the camera."""

    def set(self, param, val):
        """Set exposure time or the framerate to the camera.

        Parameters
        ----------
        param : str
            parameter key ('exposure', 'framerate'));
        val :
            value to be set (exposure time in ms, or framerate in Hz);

        """
        pass

    def read(self):
        """Grab frame from the camera and returns it as an NxM numpy array.

        Returns
        -------
        np.array
                the grabbed frame, or None if an error occurred.

        """
        return None

    def release(self):
        """Close the camera.
        """
        pass


class XimeaCamera(Camera):
    """Class for simple control of a Ximea camera.

    Uses ximea API. Module documentation `here
    <https://www.ximea.com/support/wiki/apis/Python>`_.

    """

    def __init__(self, downsampling=1, **kwargs):
        """

        Parameters
        ----------
        downsampling : int
            downsampling factor for the camera
        """
        super().__init__(**kwargs)
        self.downsampling = downsampling

        # Test if API for the camera is available
        try:
            self.cam = xiapi.Camera()
        except NameError:
            print("The xiapi package must be installed to use a Ximea camera!")

    def open_camera(self):
        """ """
        self.cam.open_device()

        self.im = xiapi.Image()
        self.cam.start_acquisition()

        if self.debug:
            print("Detected camera {}.".format(self.cam.get_device_name()))

        # If camera supports hardware downsampling (MQ013MG-ON does,
        # MQ003MG-CM does not):
        if self.cam.get_device_name() == b"MQ013MG-ON":
            self.cam.set_sensor_feature_selector("XI_SENSOR_FEATURE_ZEROROT_ENABLE")
            self.cam.set_sensor_feature_value(1)

            if self.downsampling > 1:
                self.cam.set_downsampling_type("XI_SKIPPING")
                self.cam.set_downsampling(
                    "XI_DWN_{}x{}".format(self.downsampling, self.downsampling)
                )

        self.cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE")

    def set(self, param, val):
        """

        Parameters
        ----------
        param :
            
        val :
            

        Returns
        -------

        """
        try:
            if param == "exposure":
                self.cam.set_exposure(int(val * 1000))

            if param == "framerate":
                self.cam.set_framerate(val)
        except xiapi.Xi_error:
            print("Invalid camera parameters")

    def read(self):
        """ """
        try:
            self.cam.get_image(self.im)
            frame = self.im.get_image_data_numpy()
        except xiapi.Xi_error:
            frame = None
            if self.debug:
                print("Unable to acquire frame")

        return frame

    def release(self):
        """ """
        self.cam.stop_acquisition()
        self.cam.close_device()


class AvtCamera(Camera):
    """Class for controlling an AVT camera.

    Uses the Vimba interface pymba
    (module documentation `here <https://github.com/morefigs/pymba>`_).

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, **kwargs):
        # Set timeout for frame acquisition. Give this as input?
        self.timeout_ms = 1000

        super().__init__(**kwargs)

        try:
            self.vimba = Vimba()
        except NameError:
            print("The pymba package must be installed to use an AVT camera!")

        self.frame = None

    def open_camera(self):
        """ """
        self.vimba.startup()

        # If there are multiple cameras, only the first one is used (this may
        # change):
        camera_ids = self.vimba.getCameraIds()
        if self.debug:
            if len(camera_ids) > 1:
                print(
                    "Multiple cameras detected: {}. {} wiil be used.".format(
                        camera_ids, camera_ids[0]
                    )
                )
            else:
                print("Detected camera {}.".format(camera_ids[0]))
        self.cam = self.vimba.getCamera(camera_ids[0])

        # Start camera:
        self.cam.openCamera()
        self.frame = self.cam.getFrame()
        self.frame.announceFrame()

        self.cam.startCapture()
        self.frame.queueFrameCapture()
        self.cam.runFeatureCommand("AcquisitionStart")

    def set(self, param, val):
        """

        Parameters
        ----------
        param :
            
        val :
            

        Returns
        -------

        """
        try:
            if param == "exposure":
                # camera wants exposure in us:
                self.cam.ExposureTime = int(val * 1000)

            if param == "framerate":
                # To set new frame rate for AVT cameras acquisition has to be
                # interrupted:
                # TODO Handle this in a cleaner way
                if val < 210:  # empirically found maximum frame rate
                    self.frame.waitFrameCapture(self.timeout_ms)
                    self.cam.runFeatureCommand("AcquisitionStop")
                    self.cam.endCapture()
                    self.cam.revokeAllFrames()

                    self.cam.AcquisitionFrameRate = val

                    self.cam.startCapture()
                    self.frame.queueFrameCapture()
                    self.cam.runFeatureCommand("AcquisitionStart")
        except VimbaException:
            print("Invalid value! The parameter will not be changed.")

    def read(self):
        """ """
        try:
            self.frame.waitFrameCapture(self.timeout_ms)
            self.frame.queueFrameCapture()

            raw_data = self.frame.getBufferByteData()

            frame = np.ndarray(
                buffer=raw_data,
                dtype=np.uint8,
                shape=(self.frame.height, self.frame.width),
            )

        except VimbaException:
            frame = None
            if self.debug:
                print("Unable to acquire frame")

        return frame

    def release(self):
        """ """
        self.frame.waitFrameCapture(self.timeout_ms)
        self.cam.runFeatureCommand("AcquisitionStop")
        self.cam.endCapture()
        self.cam.revokeAllFrames()
        self.vimba.shutdown()
