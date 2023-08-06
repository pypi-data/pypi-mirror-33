import numpy as np
import pandas as pd

from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import InterpolatedStimulus, CircleStimulus


# Let's define a simple protocol consisting of looms at random locations,
# of random durations and maximal sizes

# First, we inherit from the Protocol class
class LoomingProtocol(Protocol):

    # We specify the name for the dropdown in the GUI
    name = "Looming"

    def __init__(self):
        super().__init__()

        # It is nice for a protocol to be parametrized, so
        # we name the parameters we might want to change,
        # along with specifying the the default values.
        # This automatically creates a GUI to change them
        # (more elaborate ways of adding parameters are supported,
        # see the documentation of HasPyQtGraphParams)
        # TODO figure out how to integrate this with Sphinx
        self.add_params(n_looms=10, max_loom_size=40, max_loom_duration=5)

    # This is the only function we need to define for a custom protocol
    def get_stim_sequence(self):
        stimuli = []

        # A looming stimulus is an expanding circle. Stimuli which contain
        # some kind of parameter change inherit from InterpolatedStimulus
        # which allows for specifying the values of parameters of the
        # stimulus at certain time points, with the intermediate
        # values interpolated

        # Use the 3-argument version of the Python type function to
        # make a temporary class combining two classes

        LoomingStimulus = type(
            "LoomingStimulus", (InterpolatedStimulus, CircleStimulus), {}
        )

        for i in range(self.params["n_looms"]):
            # The radius is only specified at the beginning and at the
            # end of expansion. More elaborate functional relationships
            # than linear can be implemented by specifying a more
            # detailed interpolation table

            radius_df = pd.DataFrame(
                dict(
                    t=[0, np.random.rand() * self.params["max_loom_duration"]],
                    radius=[0, np.random.rand() * self.params["max_loom_size"]],
                )
            )

            # We construct looming stimuli with the radius change specification
            # and a random point of origin within the projection area
            # (specified in fractions from 0 to 1 for each dimension)
            stimuli.append(LoomingStimulus(df_param=radius_df, origin=(30, 30)))

        return stimuli


if __name__ == "__main__":
    # We make a new instance of Stytra with this protocol as the only option
    s = Stytra(protocols=[LoomingProtocol])
