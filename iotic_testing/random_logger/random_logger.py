# -*- coding: utf-8 -*-
from .data import MACHINES
from .config import RandomLoggerConfig
from .error import RandomLoggerError
from .log_generator import RandomLogGenerator
from IoticAgent import Datatypes
from IoticAgent import IOT
import collections
import logging
import random
import time

__all__ = ['RandomLogger']

logger = logging.getLogger(__name__)

LOGGER_IOT_CONFIG = 'logger'

SchemaField = collections.namedtuple('SchemaField', ('type', 'provider', 'kwargs'))
LOGGER_SCHEMA = {
    'machine': SchemaField(provider=lambda f: random.choice(MACHINES), type=Datatypes.STRING,
                           kwargs={'lang': 'en', 'description': 'Machine that sent the log'}),
    'remote': SchemaField(provider='ipv4_public', type=Datatypes.STRING,
                          kwargs={'lang': 'en', 'description': 'Remote address'}),
    'protocol': SchemaField(provider=lambda f: random.choice(('http', 'https')), type=Datatypes.STRING,
                            kwargs={'lang': 'en', 'description': 'Request protocol'}),
    'method': SchemaField(provider=lambda f: random.choice(('GET', 'POST', 'OPTIONS')), type=Datatypes.STRING,
                          kwargs={'lang': 'en', 'description': 'Request method'}),
    'duration': SchemaField(provider=lambda f: random.randrange(1, 120), type=Datatypes.DURATION,
                            kwargs={'lang': 'en', 'description': 'Request duration'}),
    'size': SchemaField(provider=lambda f: random.randrange(1, 1E6), type=Datatypes.INTEGER,
                        kwargs={'lang': 'en', 'description': 'Response size (KB)'}),
    'path': SchemaField(provider='uri_path', type=Datatypes.STRING,
                        kwargs={'lang': 'en', 'description': 'Request path'}),
    'agent': SchemaField(provider='user_agent', type=Datatypes.STRING,
                         kwargs={'lang': 'en', 'description': 'Agent'})
}


class RandomLogger:
    """An agent that generates random stuff."""

    def __init__(self, config):
        """
        Creates a new RandomLogger.

        :param config_file: an instance of random_logger.Config
        """
        assert isinstance(config, RandomLoggerConfig)
        self._config = config
        self._thing = None
        self._log_feed = None

        logger_iot_config = config.get_iot_config(LOGGER_IOT_CONFIG)
        if logger_iot_config is None:
            raise RandomLoggerError('No configuration found for agent "{}"'.format(LOGGER_IOT_CONFIG))
        self.__logger_iot_config = logger_iot_config

    def __setup_feed(self):
        """
        Defines a feed.
        """
        # TODO: does changing meta/schema every time trigger events that would be received by other agents even if
        # the meta is the same?
        with self._log_feed.get_meta() as feed_meta:
            feed_meta.set_label('Logs')
            feed_meta.set_description('Parsed logs')
        for field_name, field_definition in LOGGER_SCHEMA.items():
            self._log_feed.create_value(field_name, field_definition.type, **field_definition.kwargs)

    def start(self):
        """
        Starts logging.
        """
        with IOT.Client(config=self.__logger_iot_config) as client:
            client.register_callback_duplicate(self.duplicate_callback)
            client.register_callback_created(self.created_callback)
            client.register_callback_deleted(self.deleted_callback)
            client.register_catchall_feeddata(self.catchall_feeddata)
            self._thing = client.create_thing('Aggregator')
            try:
                self._log_feed = self._thing.get_feed('Logs')
            except KeyError:
                self._log_feed = self._thing.create_feed('logs')
            self.__setup_feed()
            generator = RandomLogGenerator(self._log_feed, LOGGER_SCHEMA)
            for item in generator:
                self._log_feed.share(item)
                time.sleep(random.randrange(1, 3))


    def duplicate_callback(self, args):
        logger.debug('duplicate_callback %s', args)

    def created_callback(self, args):
        logger.debug('created_callback %s', args)

    def deleted_callback(self, args):
        # TODO: this should react if any object that should be there is removed and abort
        logger.debug('deleted_callback %s', args)

    def catchall_feeddata(self, data):
        logger.debug('catchall_feeddata %s', data)

