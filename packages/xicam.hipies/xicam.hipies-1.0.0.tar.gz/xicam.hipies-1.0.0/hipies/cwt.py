#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import signal


def tophat2d(radius, width=10):
    """
    convolution kernel is a Mexican Hat revolved in x-plane

    Parameters
    ----------
    radius : scalar,
        peak position along the radius
    width : scalar,
        width of peak in pixels

    Returns
    -------
    ndarray
        kernel to convolve the signal
    """
    N = np.int(np.round(radius) + 3 * np.round(width) + 1)
    x = np.arange(-N, N)
    x, y = np.meshgrid(x, x)
    t = np.sqrt(x**2 + y**2) - radius
    a = 1. / np.sqrt(2 * np.pi) / width**3
    w = a * (1 - (t / width)**2) * np.exp(-t**2 / width**2 / 2.)
    return w


def cwt2d(image, domain=None, width=1, log=False):
    """
    continuous wavelets transform for finding rings in a SAXS calibration image

    Parameters
    ----------
    image: ndarray
        SAXS Calibration image
    domain: list
        [min, max] search region
    width: scalar
        width of the ring in pixels
    log: bool
        Use log of the image, default is False 
  
    Returns
    ------- 
    ndarray
        center of the detected ring
    """
    nrow, ncol = image.shape
    if domain is None:
        rmin = 0
        rmax = min(nrow, ncol)
    else:
        rmin = domain[0]
        rmax = domain[1]
    maxval = 0
    center = np.array([0, 0], dtype=np.int)
    radius = -1
    # if log is true
    if log: 
        sig = np.log(image+4).copy()
    else: sig = image.copy()

    for r in range(rmin, rmax):
        w = tophat2d(r, width)
        im2 = signal.fftconvolve(sig, w, 'same')
        if im2.max() > maxval:
            maxval = im2.max()
            center = np.unravel_index(im2.argmax(), image.shape)
            radius = r
    return center, radius
