# -*- coding: utf-8 -*-
# Copyright 2018 Alex Marchenko
# Distributed under the terms of the Apache License 2.0
"""
Distance Calculation Utilities
################################
This module provides functions for determining distances between aerial
objects (static and dynamic) which are near the surface of planet Earth.
This module makes use of compilation to speed up mathematical operations.

Tip:
    Altitudes are expected in meters, latitudes and longitudes are expected
    in degrees. By convention N and E are positive angles and S and W are
    negative angles.

See Also:
    `World Geodetic System`_
    
.. _ref: https://en.wikipedia.org/wiki/World_Geodetic_System
"""
from __future__ import absolute_import, division
import numpy as np
import numba as nb


equatorial_radius = 6378137.0               # Equatorial radius in m
polar_radius = 6356752.3                    # Polar radius in m
_a = equatorial_radius
_a2 = _a**2
_b = polar_radius
_b2 = _b**2


@nb.jit(nopython=True, nogil=True)
def lat_to_rad(degree):
    """
    Convert latitude (in degrees) to radians.

    Args:
        degree (float): Angle in degrees (e.g. +41.0 == 41.0 N).

    Returns:
        rad (float): Angle in radians
    """
    if abs(degree) > 90:
        raise ValueError("Latitudes span the range -90 <= degree <= +90")
    return degree*np.pi/180


@nb.jit(nopython=True, nogil=True)
def lon_to_rad(degree):
    """
    Convert longitude (in degrees) to radians.

    Args:
        degree (float): Angle in degrees (e.g. -122.0 == 122.0 W).

    Returns:
        rad (float): Angle in radians
    """
    if abs(degree) > 180:
        raise ValueError("Longitudes span the range -180 <= degree <= +180")
    return degree*np.pi/180

    
#@nb.jit(nopython=True, nogil=True)
def earth_radius(lat):
    """
    Compute the radius of the Earth for a given latitude.
    
    The Earth isn't exactly spherical; depending on what latitude
    an object is at, the distance from sea-level to the center of
    the Earth varies slightly.

    Args:
        lat (float): Latitude in radians

    Returns:
        radius (float): Approximate distance to sea level at the current latitude in meters
    """
    return np.sqrt(((_a2*np.cos(lat))**2 + (_b2*np.sin(lat))**2)/
                   ((_a*np.cos(lat))**2 + (_b*np.sin(lat))**2))
    
    
@nb.jit(nopython=True, nogil=True)
def to_cartesian(alt, lat, lon):
    """
    Convert altitude, latitude, and longitude to spherical coordinates.

    Distances are computed relative to the center of the earth.
    
    Args:
        alt (float): Altitude (above sea-level) in meters
        lat (float): Latitude in radians
        lon (float): Longitude in radians

    Returns:
        tup (tuple): Tuple of x, y, z coordinates in meters
    """
    r = alt + earth_radius(lat)
    x = r*np.sin(lat)*np.cos(lon)
    y = r*np.sin(lat)*np.sin(lon)
    z = r*np.cos(lat)
    return x, y, z, r

@nb.jit(nopython=True, nogil=True)
def compute_distances(xs, ys, zs):
    """
    Brute force computation of pairwise distances.

    Compute the distance between one object represented by the cartesian coordinates
    (x, y, z) and a collection of objects represented by arrays {xs}, {ys}, {zs}.
    
    Args:
    x (float): Cartesian x coordinate of source object
    y (float): Cartesian x coordinate of source object
    z (float): Cartesian x coordinate of source object
    xs (array): Cartesian x coordinates of target objects
    ys (array): Cartesian y coordinates of target objects
    zs (array): Cartesian z coordinates of target objects
    """
    n = len(xs)
    dxyz = np.empty((n, 4))
    for i in range(n):
        dx = (x - xs[i])
        dy = (y - ys[i])
        dz = (z - zs[i])
        dr = np.sqrt(dx**2 + dy**2 + dz**2)
        dxyz[i, 0] = dx
        dxyz[i, 1] = dy
        dxyz[i, 2] = dz
        dxyz[i, 3] = dr
    return dxyz
