# -*- coding: utf-8 -*-
from .error import RandomLoggerError
from IoticAgent.IOT import Config as IoticConfig

import click
import collections
import yaml


class RandomLoggerConfig:
    """
    Random logger configuration.
    """

    def __init__(self, yaml_path):
        """
        Creates a new configuration from a file stream.
        """
        with click.open_file(click.format_filename(yaml_path), 'rb') as stream:
            try:
                yaml_dict = yaml.safe_load(stream)
            except Exception as e:
                raise Exception('An error occurred while parsing {}\n{}'.format(yaml_path, e))
                sys.exit(-1)

        if 'agents' not in yaml_dict:
            raise RandomLoggerError('Missing mandatory configuration section: agents')
        if not isinstance(yaml_dict['agents'], dict):
            raise RandomLoggerError('The section agents is not a dictionary')

        self.__config = {
            'agents': collections.defaultdict()
        }

        for name, config in yaml_dict['agents'].items():
            iot_config = IoticConfig.Config()
            for section, parameters in config.items():
                for parameter, value in parameters.items():
                    iot_config.set(section, parameter, value)
            self.__config['agents'][name] = iot_config

    def get_iot_config(self, agent_name):
        """
        Returns the configuration for an IOT agent.
        :param agent_name: the name of the agent.
        :return: an IoticAgent.IOT instance or None if an agent with the specified name is not found.
        """
        return self.__config['agents'].get(agent_name, None)
