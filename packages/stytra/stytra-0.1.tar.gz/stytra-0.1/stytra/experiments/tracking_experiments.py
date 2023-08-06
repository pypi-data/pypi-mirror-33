import traceback

from PyQt5.QtCore import QTimer
from multiprocessing import Queue, Event

from stytra.calibration import CircleCalibrator

from stytra.experiments import Experiment
from stytra.gui.container_windows import (
    CameraExperimentWindow,
    TrackingExperimentWindow,
    EyeTrackingExperimentWindow,
)
from stytra.hardware.video import (
    CameraControlParameters,
    VideoWriter,
    VideoFileSource,
    CameraSource,
)

# imports for tracking

from stytra.collectors import QueueDataAccumulator
from stytra.tracking.interfaces import *
from stytra.tracking.processes import FrameDispatcher, MovingFrameDispatcher

from stytra.stimulation.estimators import (
    PositionEstimator,
    VigourMotionEstimator,
    LSTMLocationEstimator,
)

import sys


class CameraExperiment(Experiment):
    """General class for Experiment that need to handle a camera.
    It implements a view of frames from the camera in the control GUI, and the
    respective parameters.
    For debugging it can be used with a video read from file with the
    VideoFileSource class.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, *args, camera_config, camera_queue_mb=100, **kwargs):
        """
        :param video_file: if not using a camera, the video file
        file for the test input
        :param kwargs:
        """
        if camera_config.get("video_file", None) is None:
            self.camera = CameraSource(
                camera_config["type"],
                rotation=camera_config["rotation"],
                downsampling=camera_config["downsampling"],
                max_mbytes_queue=camera_queue_mb,
            )
        else:
            self.camera = VideoFileSource(
                camera_config["video_file"],
                rotation=camera_config["rotation"],
                max_mbytes_queue=camera_queue_mb,
            )

        self.camera_control_params = CameraControlParameters()

        self.gui_timer = QTimer()
        self.gui_timer.setSingleShot(False)

        super().__init__(*args, **kwargs)

    def start_experiment(self):
        """ """
        self.go_live()
        super().start_experiment()

    def make_window(self):
        """ """
        self.window_main = CameraExperimentWindow(experiment=self)
        self.window_main.show()

    def go_live(self):
        """ """
        self.gui_timer.start(1000 // 60)
        sys.excepthook = self.excepthook
        self.camera.start()

    def wrap_up(self, *args, **kwargs):
        """

        Parameters
        ----------
        *args :
            
        **kwargs :
            

        Returns
        -------

        """
        super().wrap_up(*args, **kwargs)
        self.camera.kill_event.set()
        self.camera.terminate()
        print("Camera process terminated")
        self.gui_timer.stop()

    def excepthook(self, exctype, value, tb):
        """

        Parameters
        ----------
        exctype :
            
        value :
            
        tb :
            

        Returns
        -------

        """
        traceback.print_tb(tb)
        print("{0}: {1}".format(exctype, value))
        self.camera.kill_event.set()
        self.camera.terminate()


class TrackingExperiment(CameraExperiment):
    """Abstract class for an experiment which contains tracking.

    This class is the base for any experiment that tracks behaviour (being it
    eyes, tail, or anything else).
    The general purpose of the class is handle a frame dispatcher,
    the relative parameters queue and the output queue.
    
    The frame dispatcher take two input queues:

        - frame queue from the camera;
        - parameters queue from parameter window.
    
    and it puts data in three queues:

        - subset of frames are dispatched to the GUI, for displaying;
        - all the frames, together with the parameters, are dispatched
          to perform tracking;
        - the result of the tracking function, is dispatched to a data
          accumulator for saving or other purposes (e.g. VR control).

    Parameters
    ----------
        tracking_config: dict
            containing fields:  tracking_method
                                estimator: can be vigor or lstm for embedded fish, position
                                    for freely-swimming

    Returns
    -------

    """

    tracking_methods_list = dict(
        centroid=CentroidTrackingMethod,
        angle_sweep=AnglesTrackingMethod,
        eye_threshold=ThresholdEyeTrackingMethod,
        eyes_tail=TailEyesTrackingMethod,
        fish=FishTrackingMethod,
    )

    def __init__(self, *args, tracking_config, **kwargs):
        """
        :param tracking_method: class with the parameters for tracking (instance
                                of TrackingMethod class, defined in the child);
        :param header_list: headers for the data accumulator (list of strings,
                            defined in the child);
        :param data_name:  name of the data in the final experiment log (defined
                           in the child).
        """

        self.processing_params_queue = Queue()
        self.finished_sig = Event()
        super().__init__(
            *args,
            calibrator=CircleCalibrator()
            if tracking_config["tracking_method"] == "fish"
            else None,
            **kwargs
        )

        method_name = tracking_config["tracking_method"]

        self.tracking_method = self.tracking_methods_list[method_name]()

        self.data_name = self.tracking_method.data_log_name
        self.frame_dispatcher = FrameDispatcher(
            in_frame_queue=self.camera.frame_queue,
            finished_signal=self.camera.kill_event,
            processing_parameter_queue=self.processing_params_queue,
            gui_framerate=20,
        )

        self.data_acc = QueueDataAccumulator(
            self.frame_dispatcher.output_queue,
            monitored_headers=getattr(self.tracking_method, "monitored_headers", None),
            header_list=self.tracking_method.accumulator_headers,
        )

        # Data accumulator is updated with GUI timer:
        self.gui_timer.timeout.connect(self.data_acc.update_list)
        # New parameters are sent with GUI timer:
        self.gui_timer.timeout.connect(self.send_new_parameters)
        # Tracking is reset at experiment start:
        self.protocol_runner.sig_protocol_started.connect(self.data_acc.reset)

        # start frame dispatcher process:
        self.frame_dispatcher.start()

        # This probably should happen before starting the camera process??
        if isinstance(self.tracking_method, CentroidTrackingMethod) or isinstance(
            self.tracking_method, AnglesTrackingMethod
        ):
            self.tracking_method.params.param("n_segments").sigValueChanged.connect(
                self.change_segment_numb
            )

        est_type = tracking_config.get("estimator", None)
        if est_type == "position":
            self.estimator = PositionEstimator(self.data_acc, self.calibrator)
        elif est_type == "vigor":
            self.estimator = VigourMotionEstimator(self.data_acc)
        elif est_type == "lstm":
            self.estimator = LSTMLocationEstimator(
                self.data_acc, self.asset_dir + "/swim_lstm.h5"
            )
        else:
            self.estimator = None

    # TODO probably could go to the interface, but this would mean linking
    # the data accumulator to the interface as well. Probably makes sense.
    def change_segment_numb(self):
        """ Take care of resetting the data accumulator if the number of
        segments (and therefore the points to be saved) is changed.
        """

        new_header = ["tail_sum"] + [
            "theta_{:02}".format(i)
            for i in range(self.tracking_method.params["n_segments"])
        ]
        self.data_acc.reset(header_list=new_header)

    def make_window(self):
        tail = False
        eyes = False
        if isinstance(self.tracking_method, TailTrackingMethod):
            tail = True
        if isinstance(self.tracking_method, EyeTrackingMethod):
            eyes = True

        self.window_main = TrackingExperimentWindow(
            experiment=self, tail=tail, eyes=eyes
        )

        # add streams
        self.window_main.stream_plot.add_stream(self.data_acc)

        if self.estimator is not None:
            self.window_main.stream_plot.add_stream(self.estimator.log)

        self.window_main.show()

    def send_new_parameters(self):
        """Called upon gui timeout, put tracking parameters in the relative
        queue.

        Parameters
        ----------

        Returns
        -------

        """
        self.processing_params_queue.put(self.tracking_method.get_clean_values())

    def start_protocol(self):
        """Reset data accumulator when starting the protocol."""
        # TODO camera queue should be emptied to avoid accumulation of frames!!
        # when waiting for the microscope!
        super().start_protocol()
        self.data_acc.reset()

    def end_protocol(self, *args, **kwargs):
        """Save tail position and dynamic parameters and terminate.

        Parameters
        ----------
        *args :
            
        **kwargs :
            

        Returns
        -------

        """
        if self.dc is not None:
            self.dc.add_static_data(self.data_acc.get_dataframe(), name=self.data_name)

        super().end_protocol(*args, **kwargs)
        try:
            self.estimator.reset()
            self.estimator.log.reset()
        except AttributeError:
            pass

    def set_protocol(self, protocol):
        """Connect new protocol start to resetting of the data accumulator.

        Parameters
        ----------
        protocol :
            

        Returns
        -------

        """
        super().set_protocol(protocol)
        self.protocol.sig_protocol_started.connect(self.data_acc.reset)

    def wrap_up(self, *args, **kwargs):
        """

        Parameters
        ----------
        *args :
            
        **kwargs :
            

        Returns
        -------

        """
        super().wrap_up(*args, **kwargs)
        self.frame_dispatcher.terminate()
        print("Dispatcher process terminated")

    def excepthook(self, exctype, value, tb):
        """

        Parameters
        ----------
        exctype :
            
        value :
            
        tb :
            

        Returns
        -------

        """
        traceback.print_tb(tb)
        print("{0}: {1}".format(exctype, value))
        self.finished_sig.set()
        self.camera.terminate()
        self.frame_dispatcher.terminate()


class VRExperiment(TrackingExperiment):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SwimmingRecordingExperiment(CameraExperiment):
    """Experiment where the fish is recorded while it is moving"""

    def __init__(self, *args, tracking_config, **kwargs):
        super().__init__(
            *args, calibrator=CircleCalibrator(), camera_queue_mb=500, **kwargs
        )

        self.processing_params_queue = Queue()
        self.signal_start_rec = Event()
        self.finished_signal = Event()

        self.frame_dispatcher = MovingFrameDispatcher(
            in_frame_queue=self.camera.frame_queue,
            finished_signal=self.camera.kill_event,
            signal_start_rec=self.signal_start_rec,
            processing_parameter_queue=self.processing_params_queue,
            gui_framerate=20,
        )

        self.frame_recorder = VideoWriter(
            self.directory + "/video/",
            self.frame_dispatcher.save_queue,
            self.finished_signal,
        )  # TODO proper filename

        self.motion_acc = QueueDataAccumulator(
            self.frame_dispatcher.diagnostic_queue,
            header_list=self.frame_dispatcher.diagnostic_params,
        )

        self.motion_detection_params = MovementDetectionParameters()
        self.gui_timer.timeout.connect(self.send_params)
        self.gui_timer.timeout.connect(self.motion_acc.update_list)

    def make_window(self):
        """ """
        self.window_main = TrackingExperimentWindow(
            experiment=self, tail_tracking=False
        )
        self.window_main.show()

    def go_live(self):
        """ """
        super().go_live()
        self.frame_dispatcher.start()
        self.frame_recorder.start()

    def send_params(self):
        """ """
        self.processing_params_queue.put(
            self.motion_detection_params.get_clean_values()
        )

    def start_protocol(self):
        """ """
        self.signal_start_rec.set()
        super().start_protocol()

    def wrap_up(self, *args, **kwargs):
        """

        Parameters
        ----------
        *args :
            
        **kwargs :
            

        Returns
        -------

        """
        super().wrap_up(*args, **kwargs)
        self.frame_dispatcher.terminate()
        self.frame_recorder.terminate()

    def end_protocol(self, *args, **kwargs):
        """Save tail position and dynamic parameters and terminate.

        Parameters
        ----------
        *args :
            
        **kwargs :
            

        Returns
        -------

        """
        self.finished_signal.set()
        self.frame_recorder.reset_signal.set()
        super().end_protocol(*args, **kwargs)
