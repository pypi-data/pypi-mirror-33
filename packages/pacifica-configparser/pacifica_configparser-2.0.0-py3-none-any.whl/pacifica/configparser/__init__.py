#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ConfigParser logic for Pacifica configurations."""
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser, FileType
from copy import deepcopy
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover only one version of python will cover this
    from configparser import SafeConfigParser
import six


class ConfigArgParser(object):
    """Pulls command line defaults from config file."""

    @staticmethod
    def get_safe_parser(conf_file):
        """Return a safe config parser in versioned way."""
        config = SafeConfigParser()
        # seems python 2 uses readfp and python 3 uses read_file
        # but pylint calls this as a deprecated method
        # pylint: disable=deprecated-method
        if six.PY2:  # pragma: no cover only with python 2
            config.readfp(conf_file)
        else:  # pragma: no cover only with python 3
            config.read_file(conf_file)
        # pylint: enable=deprecated-method
        return config

    @staticmethod
    def get_action_group_titles(parser):
        """Get the action group titles from a parser object."""
        # pylint: disable=protected-access
        return [x.title for x in parser._action_groups[2:] if hasattr(x, 'title')]
        # pylint: enable=protected-access

    @staticmethod
    def update_defaults(defaults, conf_file, action_groups):
        """Update the defaults from a config parser."""
        def_copy = deepcopy(defaults)
        config = ConfigArgParser.get_safe_parser(conf_file)
        for config_group in action_groups:
            def_copy.update(dict(config.items(config_group)))
        def_copy.update(dict(config.items('DEFAULT')))
        return def_copy

    @staticmethod
    def configargparser(parser, defaults, def_conf_file, env_prefix, argv=False):
        """Use defaults found in config file and return a Namespace."""
        if not argv:  # pragma: no cover within pytest
            argv = sys.argv
        config_parser = ArgumentParser(
            description='parse out the config file', add_help=False)
        config_parser.add_argument(
            '-c', '--config', dest='conf_file', type=FileType('r'),
            help='Specify config file', metavar='FILE',
            default=open(def_conf_file)
        )
        args, remaining_argv = config_parser.parse_known_args(argv)
        action_group_titles = ConfigArgParser.get_action_group_titles(parser)
        def_copy = ConfigArgParser.update_defaults(
            defaults, args.conf_file, action_group_titles)
        for key in def_copy.keys():
            env_key = '{}_{}'.format(env_prefix.upper(), key.upper())
            if os.getenv(env_key, False):
                def_copy[key] = os.getenv(env_key)
        parser.set_defaults(**def_copy)
        return parser.parse_args(remaining_argv)
