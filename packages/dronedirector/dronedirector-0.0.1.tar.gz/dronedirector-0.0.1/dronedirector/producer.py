# -*- coding: utf-8 -*-
# Copyright 2018 Alex Marchenko
# Distributed under the terms of the Apache License 2.0
"""
Kafka Producer
#################
This module provides a simple interface for generating messages from
:class:`~dronedirector.aerial.Drone`s
about their location (altitude, latitude, longitude). An 
Avro schema is provided for :class:`~dronedirector.aerial.Drone` messages.
"""
from __future__ import print_function
try:
    import confluent_kafka as ck
except ImportError:
    raise ImportError("Confluent Kafka Python client not available")
try:
    from confluent_kafka import avro
except ImportError:
    raise ImportError("Please install Avro to use this module")
import time


# value schema
drone_schema_str = """
{
    "namespace": "dronedirector.drones",
    "name": "drone",
    "type": "record",
    "fields": [
        {
            "name": "uid",
            "type": "string"
        },
        {
            "name": "region",
            "type": "string"
        },
        {
            "name": "dronetime",
            "type": "string"
        },
        {
            "name": "altitude",
            "type": "double"
        },
        {
            "name": "latitude",
            "type": "double"
        },
        {
            "name": "longitude",
            "type": "double"
        }
    ]
}"""


def fly_avro_drones(bootstrap_servers, schema_registry_url, nmessages, default_value_schema_str=drone_schema_str,
               producer_dict_kwargs=None, topic_name="drones_raw", time_delay=0, drones=None):
    """
    A simple example of sending structured messages from drones to a message broker.

    Args:
        bootstrap_servers (str): Comma separated string of Kafka servers
        schema_registry_url (str): Schema registry URL
        nmessages (int): Number of messages to send
        default_value_schema_str (str): String Avro schema compatible with mdrone messages
        producer_dict_kwargs (dict): Optional keyword arguments for producer
        topic_name (str): Topic name to which drone messages will be sent
        time_delay (int): Delay time between cycles when producing messages
        drones (iterable): Iterable of drones from which to generate messages

    Tip:
        Schemas should match the messages sent by drones.
    """
    pdk = {'bootstrap.servers': bootstrap_servers,
           'schema.registry.url': schema_registry_url},
    if isinstance(producer_dict_kwargs, dict):
        pdk.update(producer_dict_kwargs)
    producer = avro.AvroProducer(pdk, default_value_schema=avro.loads(default_value_schema_str))
    z = len(str(nmessages))            # Pretty print cycle number for logging
    for i in range(nmessages):
        print("====MESSAGE SET {}====".format(str(i).zfill(z)))
        for drone in drones:
            msg = drone.message()
            print(msg)
            producer.produce(topic=topic_name, value={k: getattr(msg, k) for k in msg._fields})
        time.sleep(time_delay)
    producer.flush()


def fly_drones(bootstrap_servers, nmessages, producer_dict_kwargs=None,
               topic_name="drones_raw", time_delay=0, drones=None):
    """
    A simple example of sending drones that send JSON messages to the message broker.

    Args:
        bootstrap_servers (str): Comma separated string of Kafka servers
        nmessages (int): Number of messages to send
        producer_dict_kwargs (dict): Optional keyword arguments for producer
        topic_name (str): Topic name to which drone messages will be sent
        time_delay (int): Delay time between cycles when producing messages
        drones (iterable): Iterable of drones from which to generate messages
    """
    pdk = {'bootstrap.servers': bootstrap_servers}
    if isinstance(producer_dict_kwargs, dict):
        pdk.update(producer_dict_kwargs)
    producer = ck.Producer(pdk)
    z = len(str(nmessages))            # Pretty print cycle number for logging
    for i in range(nmessages):
        print("====MESSAGE SET {}====".format(str(i).zfill(z)))
        for drone in drones:
            msg = drone.message()
            print(msg)
            producer.produce(topic_name, str({k: getattr(msg, k) for k in msg._fields}))
        time.sleep(time_delay)
    producer.flush()
