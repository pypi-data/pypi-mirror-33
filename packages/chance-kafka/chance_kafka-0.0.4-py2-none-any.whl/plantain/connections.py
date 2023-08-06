#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: plantain/connections.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.04.2018
from functools import wraps
from kafka import KafkaProducer

from plantain.consumer import Consumer


class KafkaConnection(object):
    """Class for kafka connection
    """
    bootstrap_servers = None
    producer = None

    @classmethod
    def connect(cls, bootstrap_servers):
        """Get server configs and create producer

        Args:
            bootstrap_servers: ([str]) a list of server addr
            default_producer: (bool) whether producer is created.
        """
        cls.bootstrap_servers = bootstrap_servers

        cls.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    @classmethod
    def close(cls):
        """Close producer
        """
        cls.producer.close()
        cls.producer = None

    @classmethod
    def with_producer(cls):
        """Decorator for introducing producer

        Wrap the function with the static producer.

        Example:

        .. code-block:: python

            @with_producer
            def A(some_arguments, producer):
                pass

        Notice that only in keywords can you pass your own producer rather than
        the given, or a TypeError will raise for multiple arguments
        of producer passed into the same function. In other works, following
        code will raise a TypeError:

        .. code-block:: python

            @with_producer
            def A(some_arguments, producer):
                pass

            A('test', your_own_producer) # Raise TypeError
            A('test', producer=your_own_producer) # Safe

        Return:
            a wrapped func
        """
        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                producer = kwargs.pop('producer', cls.producer)
                kwargs['producer'] = producer

                return func(*args, **kwargs)

            return wrapper
        return decorator

    @classmethod
    def create_consumer(cls, topics, timeout, offset, group_id):
        """Create consumer with given args

        Args:
            topic: (str / [str]) a list of str or a str as listened topics
            timeout: (int or None) the timeout before close consumer, or not
            close when is set to None.
            offset: (str) the offset in the topic, 'latest' or 'earlist'.
            group_id: (str) the group of consumer

        Return:
            (consumer.Consumer)
        """
        if isinstance(topics, basestring):
            topics = [topics]

        return Consumer(
            cls.bootstrap_servers, *topics, timeout_ms=timeout, offset=offset,
            group_id=group_id
        )
