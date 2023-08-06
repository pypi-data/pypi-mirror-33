"""
    Author: Andreas Kist
"""

import numpy as np
from skimage.filters import threshold_local, threshold_otsu
import cv2


def _pad(im, padding=0, val=0):
    """Lazy function for padding image

    Parameters
    ----------
    im :

    val :
        return: (Default value = 0)
    padding :
         (Default value = 0)

    Returns
    -------

    """
    padded = np.lib.pad(
        im,
        ((padding, padding), (padding, padding)),
        mode="constant",
        constant_values=((val, val), (val, val)),
    )
    return padded


def _local_thresholding(im, padding=2, block_size=17, offset=70):
    """Local thresholding

    Parameters
    ----------
    im :
        The camera frame with the eyes
    padding :
        padding of the camera frame (Default value = 2)
    block_size :
        param offset: (Default value = 17)
    offset :
         (Default value = 70)

    Returns
    -------
    type
        thresholded image

    """
    padded = _pad(im, padding, im.min())
    return padded > threshold_local(padded, block_size=block_size, offset=offset)


def _fit_ellipse(thresholded_image):
    """Finds contours and fits an ellipse to thresholded image

    Parameters
    ----------
    thresholded_image :
        Binary image containing two eyes

    Returns
    -------
    type
        When eyes were found, the two ellipses, otherwise False

    """
    _, contours, hierarchy = cv2.findContours(
        thresholded_image.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) >= 2:

        # Get the two largest ellipses (i.e. the eyes, not any dirt)
        contours = sorted(contours, key=lambda c: c.shape[0], reverse=True)[:2]
        # Sort them that first ellipse is always the left eye (in the image)
        contours = sorted(contours, key=np.max)

        # Fit the ellipses for the two eyes
        if len(contours[0]) > 4 and len(contours[1]) > 4:
            e = [cv2.fitEllipse(contours[i]) for i in range(2)]
            return e
        else:
            return False
        # except cv2.error:
        #     print('unknown error')
        #     return False

    else:
        # Not at least two eyes + maybe dirt found...
        return False


# TODO: function for scaling/filtering/invert should be unique for both
# tail and eye tracking
def trace_eyes(im, wnd_pos, wnd_dim, threshold, image_scale, filter_size, color_invert):
    """

    Parameters
    ----------
    im :
        image (numpy array);
    win_pos :
        position of the window on the eyes (x, y);
    win_dim :
        dimension of the window on the eyes (w, h);
    threshold :
        threshold for ellipse fitting (int).
    wnd_pos :
        
    wnd_dim :
        
    image_scale :
        
    filter_size :
        
    color_invert :
        

    Returns
    -------

    """
    PAD = 0

    cropped = _pad(
        im[
            wnd_pos[0] : wnd_pos[0] + wnd_dim[0], wnd_pos[1] : wnd_pos[1] + wnd_dim[1]
        ].copy(),
        padding=PAD,
        val=255,
    )

    thresholded = (cropped < threshold).astype(np.uint8)

    # try:
    e = _fit_ellipse(thresholded)
    if e is False:
        print("I don't find eyes here...")
        e = (np.nan,) * 10
    else:
        e = e[0][0] + e[0][1] + (e[0][2],) + e[1][0] + e[1][1] + (e[1][2],)

    return np.array(e)
