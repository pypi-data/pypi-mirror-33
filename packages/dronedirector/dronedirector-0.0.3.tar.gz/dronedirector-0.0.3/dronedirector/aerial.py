# -*- coding: utf-8 -*-
# Copyright 2018 Alex Marchenko
# Distributed under the terms of the Apache License 2.0
"""
Aerial Objects
#################
This module provides some simple classes that are used to simulate flying
drones and other objects. The

Tip:
    Altitudes are expected in meters, latitudes and longitudes are expected
    in degrees. By convention N and E are positive angles and S and W are
    negative angles.

See Also:
    `World Geodetic System`_
    
.. _ref: https://en.wikipedia.org/wiki/World_Geodetic_System
"""
from __future__ import absolute_import
import six
import uuid
import json
import types
import numpy as np
from datetime import datetime
from itertools import cycle


dtfmt = "%Y%m%d%H%M%S%f"


class AerialObject(object):
    """
    Base class for aerial objects.

    Aerial objects can be static or dynamic but must define something
    about their location (latitude, longitude) and how tall they are/how
    high up they fly. An example of a static aerial object (like a tree
    or building) is given below. Note that :class:`~dronedirector.aerial.AerialObject`s
    must at minimum define alitutde, latitude, and longitude.

    .. code:: Python

        class CaliRedwood(AerialObject):
            # Example of a completely static object
            def __init__(self):
                super(AerialObject, self).__init__(altitude=itertools.cycle([100.0]),
                                                   latitude=itertools.cycle([37.8716]),
                                                   longitude=itertools.cycle([-122.2727]))
    """
    def message(self):
        """
        Get the current coordinates of the object as a JSON message.

        Returns:
            text (str): JSON formatted message
        """
        return json.dumps(dict(altitude=next(self.altitude),
                               latitude=next(self.latitude),
                               longitude=next(self.longitude)))

    def __init__(self, altitude, latitude, longitude):
        if not all(isinstance(i, (types.GeneratorType, cycle)) for i in (altitude, latitude, longitude)):
            raise TypeError("Altitude, latitude, and longitude must be generators")
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude


class Drone(AerialObject):
    """
    Base class for drones.

    .. code:: Python

        drone = Drone(altitude=itertools.cycle([1000.0]),
                      latitude=itertools.cycle([41.0]),
                      longitude=itertools.cycle(np.sin(np.arange(0, 2*np.pi, np.pi/(360*50)))),
                      region="New York County")

    Args:
        altitude: Generator that yields altitude(s)
        latitude: Generator that yields latitude(s)
        longitude: Generator that yields longitude(s)
        region: Region (coarse location) identifier
        uid: Unique identifier
    """
    def message(self):
        """
        Get the current coordinates of the object as a JSON message.

        Returns:
            text (str): JSON formatted message
        """
        return json.dumps(dict(altitude=next(self.altitude),
                               latitude=next(self.latitude),
                               longitude=next(self.longitude),
                               uid=self.uid.hex,
                               region=self.region,
                               dronetime=datetime.now().strftime(dtfmt)))

    def __init__(self, altitude, latitude, longitude, region, uid=None):
        super(Drone, self).__init__(altitude, latitude, longitude)
        self.uid = uuid.uuid4() if uid is None else uid
        self.region = region


class SinusoidalDrone(Drone):
    """
    A drone that circumnavigates the Earth sinusoidally at a given altitude
    and latitude and with a given angular speed.

    Args:
        alt (float): Drone's constant altitude
        lat (float): Drone's constant latitude
        region: Region (coarse location) identifier
        uid: Unique identifier
        speed (float): Fraction of a (longitudinal) degree moved per second
    """
    def __init__(self, alt, lat, region, uid=None, speed=0.02):
        altitude = cycle([alt])
        latitude = cycle([lat])
        longitude = cycle(np.sin(np.arange(0, 2*np.pi, np.pi/360*speed)))
        super(SinusoidalDrone, self).__init__(altitude=altitude, latitude=latitude,
                                              longitude=longitude, uid=uid, region=region)
