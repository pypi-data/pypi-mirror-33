# Drone Director
A simple Python package for simulating aerial drones. The package has an API
for generating both static and dynamic objects that have altitude, latitude,
and longitude attributes. Functions are available for calculating relative
distances between objects. If the Confluent Kafka client is present (with
a corresponding server running somewhere), this package provides an API
for producing messages about the drones.

[![Build Status](https://travis-ci.org/avmarchenko/dronedirector.svg?branch=master)](https://travis-ci.org/avmarchenko/dronedirector)
[![Build status](https://ci.appveyor.com/api/projects/status/w29k2lpt1ala7anm/branch/master?svg=true)](https://ci.appveyor.com/project/avmarchenko/dronedirector/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/avmarchenko/dronedirector/badge.svg?branch=master)](https://coveralls.io/github/avmarchenko/dronedirector?branch=master)
