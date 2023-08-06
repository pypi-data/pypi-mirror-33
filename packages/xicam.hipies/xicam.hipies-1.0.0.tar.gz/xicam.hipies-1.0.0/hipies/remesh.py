#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
from .warp_image import warp_image, pixel2q, x2angles
try:
    import cWarpImage
    remesh_fcn = cWarpImage.warp_image
except ImportError:
    remesh_fcn = warp_image


def remesh(image,
           geometry,
           alphai,
           out_range=None,
           res=None,
           coord_sys='qp_qz'):
    """
    Redraw the GI Image in (qp, qz) coordinates.

    Parameters:
    -----------
    image: ndarray, 
        detector image 
    geometry: pyFAI Geometry
        PONI, Pixel Size, Sample Det dist etc
    alphai: scalar, deg
        angle of incedence
    out_range: list, optional
        [[left, right],[lower, upper]] for the output image
    res: list, optional
        resolution of the output image
    coord_sys: str
        'qp_qz', 'qy_qz' or 'theta_alpha' 
    Returns
    -------
    qimage: ndarray
        remeshed/warped image
    xcrd: ndarray
        x-coords of warped image
    ycrd: ndarray
        y-coords of warped image
    """
    rows, cols = image.shape
    center = np.array([geometry.get_poni2(), geometry.get_poni1()])
    pixel = [geometry.get_pixel1(), geometry.get_pixel2()]
    dist = geometry.get_dist()
    # convert wavelen to nanomters
    wavelen = geometry.get_wavelength() * 1.0E+09
    k0 = 2 * np.pi / wavelen

    if coord_sys is None:
        coord_sys = 'qp_qz'

    if res is None:
        res = [rows, cols]
    else:
        if not len(res) == 2:
            sys.stderr.write('resolution should a sequence of two integers')
            exit(1)

    if out_range is None:
        # coordinates for detector corners
        coord = np.multiply([[0, cols], [0, rows]], pixel) - center[:,np.newaxis]
        if coord_sys == 'qp_qz' or coord_sys == 'qy_qz':
            qx, qy, qz = pixel2q(coord[0, :], coord[1, :], dist, alphai, k0)
            qp = np.sign(qy) * np.sqrt(qx**2 + qy**2)
            qz = np.linspace(qz[0], qz[1], res[0])
            qp = np.linspace(qp[0], qp[1], res[1])
            ycrd = qz
            if coord_sys == 'qp_qz':
                xcrd, ycrd = np.meshgrid(qp, qz)
                qp, qz = xcrd, ycrd
            else:
                xcrd, ycrd = np.meshgrid(qy, qz)
                qp, qz = np.meshgrid(qp, qz)
                

        if coord_sys == 'theta_alpha':
            theta, alpha = x2angles(coord[0,:], coord[1,:], dist)

            xcrd = np.linspace(theta[0], theta[1], res[1])
            ycrd = np.linspace(alpha[0], alpha[1], res[0])
            xcrd, ycrd = np.meshgrid(xcrd, ycrd)

            qx = k0 * (np.cos(alpha) * np.cos(theta) - np.cos(alphai))
            qy = k0 * (np.cos(alpha) * np.sin(theta))
            qz = k0 * (np.sin(alpha) + np.sin(alphai))
            qp = np.sign(qy) * np.sqrt(qx**2 + qy**2)
            qz = np.linspace(qz[0], qz[1], res[0])
            qp = np.linspace(qp[0], qp[1], res[1])
            qp, qz = np.meshgrid(qp, qz)
            
    else:
        if coord_sys == 'qp_qz':
            qp = np.linspace(out_range[0][0], out_range[0][1], res[1])
            qz = np.linspace(out_range[1][0], out_range[1][1], res[0])
            qp, qz = np.meshgrid(qp, qz)
            xcrd, ycrd = qp, qz

        elif coord_sys == 'qy_qz':
            qz = np.array(out_range[1])
            qy = np.array(out_range[0])
            xcrd, ycrd = np.meshgrid(qy, qz)
            sin_al = qz/k0 - np.sin(alphai)
            cos_al = np.sqrt(1. - sin_al**2)
            sin_th = qy/k0/cos_al
            cos_th = np.sqrt(1. - sin_th**2)
            qx = k0 * (cos_al * cos_th - np.cos(alphai))
            qp = np.sign(qy) * np.sqrt(qx**2 + qy**2)
            qp = np.linspace(qp[0], qp[1], res[1])
            qz = np.linspace(qz[0], qz[1], res[0])
            qp, qz = np.meshgrid(qp, qz)
            

        elif coord_sys == 'theta_alpha':
            xcrd = np.array(out_range[0])
            ycrd = np.array(out_range[1])
            qx = k0 * (np.cos(ycrd) * np.cos(xcrd) - np.cos(alphai))
            qy = k0 * np.cos(ycrd) * np.sin(xcrd)
            qz = k0 * (np.sin(ycrd) + np.sin(alphai))
            qp = np.sign(qy) * np.sqrt(qx**2 + qy**2)
            qp = np.linspace(qp[0], qp[1], res[1])
            qz = np.linspace(qz[0], qz[1], res[0])
            qp, qz = np.meshgrid(qp, qz)
            xcrd = np.linspace(xcrd[0], xcrd[1], res[1])
            ycrd = np.linspace(ycrd[0], ycrd[1], res[0])
            xcrd, ycrd = np.meshgrid(xcrd, ycrd)
            
    qimage = remesh_fcn(image, qp, qz, pixel, center, alphai, k0, dist, 0)
    return qimage, xcrd, ycrd
