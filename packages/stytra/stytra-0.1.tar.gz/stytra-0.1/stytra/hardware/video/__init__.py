"""
Module to interact with video surces as cameras or video files. It also
implement video saving
"""

import numpy as np
import glob

from multiprocessing import Queue, Event
from multiprocessing.queues import Empty, Full
from stytra.utilities import FrameProcessor
from arrayqueues.shared_arrays import TimestampedArrayQueue

from stytra.hardware.video.cameras import XimeaCamera, AvtCamera
from stytra.hardware.video.write import VideoWriter
from stytra.hardware.video.interfaces import CameraControlParameters


class VideoSource(FrameProcessor):
    """Abstract class for a process that generates frames, being it a camera
    or a file source. A maximum size of the memory used by the process can be
    set.
    
    **Input Queues:**

    self.control_queue :
        queue with control parameters for the source, e.g. from a
        :class:`CameraControlParameters <.interfaces.CameraControlParameters>`
        object.


    **Output Queues**

    self.frame_queue :
        TimestampedArrayQueue from the arrayqueues module
        where the frames read from the camera are sent.


    **Events**

    self.kill_signal :
        When set kill the process.


    Parameters
    ----------
    rotation : int
        n of times image should be rotated of 90 degrees
    max_mbytes_queue : int
        maximum size of camera queue (Mbytes)

    Returns
    -------

    """

    def __init__(self, rotation=False, max_mbytes_queue=100):
        """ """
        super().__init__()
        self.rotation = rotation
        self.control_queue = Queue()
        self.frame_queue = TimestampedArrayQueue(max_mbytes=max_mbytes_queue)
        self.kill_event = Event()


class CameraSource(VideoSource):
    """Process for controlling a camera.

    Cameras currently implemented:
    
    ======== ===========================================
    Ximea    Add some info
    Avt      Add some info
    ======== ===========================================

    Parameters
    ----------
    camera_type : str
        specifies type of the camera (currently supported: 'ximea', 'avt')
    downsampling : int
        specifies downsampling factor for the camera.

    Returns
    -------

    """

    camera_class_dict = dict(ximea=XimeaCamera, avt=AvtCamera)
    """ dictionary listing classes used to instantiate camera object."""

    def __init__(self, camera_type, *args, downsampling=1, **kwargs):
        """ """
        super().__init__(*args, **kwargs)

        self.camera_type = camera_type
        self.downsampling = downsampling
        self.cam = None

    def run(self):
        """
        After initializing the camera, the process constantly does the
        following:

            - read control parameters from the control_queue and set them;
            - read frames from the camera and put them in the frame_queue.


        """
        try:
            CameraClass = self.camera_class_dict[self.camera_type]
            self.cam = CameraClass(debug=True, downsampling=self.downsampling)
        except KeyError:
            print("{} is not a valid camera type!".format(self.camera_type))
        self.cam.open_camera()
        while True:
            # Kill if signal is set:
            self.kill_event.wait(0.0001)
            if self.kill_event.is_set():
                break

            # Try to get new parameters from the control queue:
            if self.control_queue is not None:
                try:
                    param, value = self.control_queue.get(timeout=0.0001)
                    self.cam.set(param, value)
                except Empty:
                    pass

            # Grab the new frame, and put it in the queue if valid:
            arr = self.cam.read()
            if arr is not None:
                # If the queue is full, arrayqueues should print a warning!
                if self.rotation:
                    arr = np.rot90(arr, self.rotation)
                self.frame_queue.put(arr)

        self.cam.release()


class VideoFileSource(VideoSource):
    """A class to stream videos from a file to test parts of
    stytra without a camera available.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, source_file=None, loop=True, framerate=300, **kwargs):
        super().__init__(**kwargs)
        self.source_file = source_file
        self.loop = loop

    def run(self):
        """ """
        # If the file is a Ximea Camera sequence, frames in the  corresponding
        # folder are read.
        import cv2

        im_sequence_flag = self.source_file.split(".")[-1] == "xiseq"
        if im_sequence_flag:
            frames_fn = glob.glob("{}_files/*".format(self.source_file.split(".")[-2]))
            frames_fn.sort()
            k = 0
        else:
            cap = cv2.VideoCapture(self.source_file)
        ret = True

        while ret and not self.kill_event.is_set():
            if self.source_file.split(".")[-1] == "xiseq":
                frame = cv2.imread(frames_fn[k])
                k += 1
                if k == len(frames_fn) - 2:
                    ret = False
            else:
                ret, frame = cap.read()

            if ret:
                self.frame_queue.put(frame[:, :, 0])
            else:
                if self.loop:
                    if im_sequence_flag:
                        k = 0
                    else:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret = True
                else:
                    break
            self.update_framerate()
        return


if __name__ == "__main__":
    process = CameraSource("ximea")
    process.start()
    process.kill_event.set()
