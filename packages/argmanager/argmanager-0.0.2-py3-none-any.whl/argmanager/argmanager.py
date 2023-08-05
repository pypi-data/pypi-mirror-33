#!/usr/bin/env python3
# coding: utf-8

"""
File: argmanager.py
Author: Olivier BERNARD
Email: obernard78+github@gmail.com
Github: https://github.com/obernard/argmanager
Description:
    This module adds a layer to argparse, by providing an ArgumentManager class.

    This class inherits from ArgumentParser and enables the definition of options
    in configuration files.
"""

from argparse import ArgumentParser
from configparser import ConfigParser
import logging
from os import environ
from os.path import isdir, isfile
from os.path import join as path_join


logging.basicConfig()
LOGGER = logging.getLogger(__name__)


class ArgumentManager(ArgumentParser):
    """
    Wrapper around argparse.ArgumentParser that handles options definitions in
    configuration files.

    Keyword Arguments:
        - config_file_name -- The name of the configuration file to parse (default: config.conf).
        - search_path -- The list of path in which the config files can be
                         (default: [~/.config/, ~/, ./]). The last one will have prevalence 
                         over the others.
        - sections -- the list of sections to be parsed in the configuration files 
                      (default: [default]). The last on will have prevalence over 
                      the others.
        - Arguments of argparse.ArgumentParser.
    """

    def __init__(self, config_file_name='config.conf', search_path=None, sections=None, **args):
        super().__init__(**args)
        if not search_path:
            search_path = [path_join(environ['HOME'], '.config'), environ['HOME'], '.']
        if not sections:
            sections = ['default']
        self.config_file_name = config_file_name
        self.search_path = search_path
        self.sections = sections
        self.config_value = {}

    def _read_config_files(self):
        config = ConfigParser()
        LOGGER.debug('search path={}'.format(self.search_path))
        for path in self.search_path:
            if not isdir(path):
                continue
            LOGGER.debug('Found search_path: {}'.format(path))
            candidate = path_join(path, self.config_file_name)
            if not isfile(candidate):
                continue
            LOGGER.debug('Found candidate config file: {}'.format(candidate))
            config.read(candidate)
            for section in self.sections:
                for key in config[section]:
                    self.config_value[key] = config[section][key]

    def parse_args(self, args=None, namespace=None):
        self._read_config_files()
        LOGGER.debug('self.config_value={}'.format(self.config_value.keys()))
        args = super().parse_args(args, namespace)
        options = args._get_kwargs()
        for option, value in options:
            if value is None:
                try:
                    setattr(args, option, self.config_value[option])
                except KeyError:
                    continue
        return args


# pylint: disable=C0111
def main():
    pass


if __name__ == '__main__':
    main()
