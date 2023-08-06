#!/usr/bin/env python
import json
import time

import redis

from .exceptions import RedisConnectorWrongConfiguration
from .constants import (
    WRONG_CONFIG_CHANNELS_SHOULD_BE_LIST_TUPLE,
    WRONG_CONFIG_CHANNEL_NAME_SHOULD_BE_STR,
)


class RedisConnector:

    def __init__(self, host, port, channels, service_name):
        """Init method for RedisConnector

        :param host: the redis host yu will connect to.
        :type host: str

        :param port: redis port.
        :type port: int

        :param channels: the name of the redis queue you need to subscribe to.
        :type channels: string

        :param service_name: The name of the service is connecting to the queue.
        :type service_name: type

        :rtype: None
        """
        self._redis = redis.StrictRedis(host=host, port=port)
        self.pub_sub = self._redis.pubsub()

        if isinstance(channels, (list, tuple)):
            for channel in channels:
                if not isinstance(channel, str):
                    raise RedisConnectorWrongConfiguration(WRONG_CONFIG_CHANNEL_NAME_SHOULD_BE_STR)
        else:
            raise RedisConnectorWrongConfiguration(WRONG_CONFIG_CHANNELS_SHOULD_BE_LIST_TUPLE)

        self.service_name = service_name
        self.ping_channel = 'ping:{}'.format(self.service_name)
        channels.append(self.ping_channel)

        for channel in channels:
            if not isinstance(channel, str):
                raise RedisConnectorWrongConfiguration(WRONG_CONFIG_CHANNEL_NAME_SHOULD_BE_STR)
            self.pub_sub.subscribe(channel)

    def __enter__(self):
        """Implement with statement."""
        return self

    def __exit__(self, *args, **kwargs):
        """Implement with statement."""
        return self.close()

    def close(self):
        return self.pub_sub.close()

    def ping(channel, self):
        """Will ping to the channel, to see how many consumers connected."""
        return self.publish(channel, {'target': None, 'message': 'ping'})

    def publish(self, channel, message):
        """Will publish the message to the channel you are subscribed to.

        :param message: message you want to publish.
        :type message: str

        :rtype: None
        """
        return self._redis.publish(channel, json.dumps(message))

    def subscribe(self, exec_function):
        """Subscribes to the redis queue.

        :param exec_function:
            function that will be executed when the message arrives with the data extracted as only arg
        :type exec_function: executable

        :rtype: None
        """
        message = self.pub_sub.get_message()
        if message:
            data = message['data']
            if message['type'] == 'message':
                data = json.loads(data.decode('utf8').replace("'", '"'))

                # ping messages will be ignored, redis will simply return with the number of subscribers on
                # that channel
                if data.get('message') == 'ping':
                    pass
                else:
                    # No target means promiscuous mode for that message, no lock will be used
                    target = data.pop('target', None)
                    if target is None:
                        exec_function(data)
                    elif target == self.service_name:
                        if self._acquire_lock(data['message_id']):
                            exec_function(data)

    def _acquire_lock(self, message_id, lock_timeout=10):
        """Will lock the redis key for a max of 10 seconds,
        if the lock is free then it will process the message inmediatly, leaving it locked for the
        lock_timeout in all the cases, thus not allowing to process the messege to any other service.

        :param lock_timeout: Time in seconds the lock will be set before release
        :type lock_timeout: int

        :rtype: bool
        """
        expire_time = time.time() + (lock_timeout * 2 / 3)
        while time.time() < expire_time:
            if self._redis.setnx(message_id, expire_time):
                self._redis.expire(message_id, lock_timeout)
                return True

            elif not self._redis.ttl(message_id):
                self._redis.expire(message_id, lock_timeout)

            time.sleep(0.001)
        return False
