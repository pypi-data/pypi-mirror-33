#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import numpy as np

def warp_image(image, qp, qz, pixel, center, alphai, k0, dist, method):
    # find reverse map for every pair or qp,qz
    sin_al = qz / k0 - np.sin(alphai)
    cos_al = np.sqrt(1 - sin_al**2)
    with np.errstate(divide='ignore'):
        tan_al = sin_al / cos_al

    cos_ai = np.cos(alphai)
    with np.errstate(divide='ignore'):
        cos_th = (cos_al**2 + cos_ai**2 - (qp / k0)**2) / (2 * cos_al * cos_ai)
    with np.errstate(invalid='ignore'):
        sin_th = np.sign(qp) * np.sqrt(1 - cos_th**2)
    with np.errstate(divide='ignore', invalid='ignore'):
        tan_th = sin_th / cos_th

    map_x = ((tan_th * dist + center[0]) / pixel[0])
    with np.errstate(divide='ignore'):
        map_y = ((tan_al * dist / cos_th + center[1]) / pixel[1])

    # get forbidden locations
    mask = np.isnan(map_x) | np.isnan(map_y)
    rows,cols = image.shape

    # remove nans
    map_x[mask] = 0
    map_y[mask] = 0

    # mask out of range values
    mask[(map_x < 0)|(map_x > cols-1)] = True
    mask[(map_y < 0)|(map_y > rows-1)] = True

    # remove out of range values
    map_x[mask] = 0
    map_y[mask] = 0

    # flatten and convert to list of integers
    map_x = map_x.astype(int).ravel().tolist()
    map_y = map_y.astype(int).ravel().tolist()
    q_image = np.fromiter([image[i,j] for i,j in zip(map_y,map_x)], np.float).reshape(qp.shape)
    q_image[mask] = 0.
    return q_image


def x2angles(x, y, d):
    s1 = np.sqrt(d**2 + x**2)
    theta = np.arctan2(x, d)
    alpha = np.arctan2(y, s1)
    return theta, alpha


def pixel2q(x, y, d, alphai, k0):
    s1 = np.sqrt(x**2 + d**2)
    s2 = np.sqrt(s1**2 + y**2)
    sin_th = x / s1
    cos_th = d / s1
    sin_al = y / s2
    cos_al = s1 / s2
    qx = k0 * (cos_al * cos_th - np.cos(alphai))
    qy = k0 * cos_al * sin_th
    qz = k0 * (sin_al + np.sin(alphai))
    return qx, qy, qz
