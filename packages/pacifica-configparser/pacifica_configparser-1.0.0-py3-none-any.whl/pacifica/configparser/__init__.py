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


# pylint: disable=too-few-public-methods
class ConfigArgParser(object):
    """Pulls command line defaults from config file."""

    @staticmethod
    def configargparser(parser, defaults, def_conf_file, env_prefix, argv=False):
        """Use defaults found in config file and return a Namespace."""
        if not argv:  # pragma: no cover within pytest
            argv = sys.argv
        def_copy = deepcopy(defaults)
        config_parser = ArgumentParser(
            description='parse out the config file', add_help=False)
        config_parser.add_argument(
            '-c', '--config', dest='conf_file', type=FileType('r'),
            help='Specify config file', metavar='FILE',
            default=open(def_conf_file)
        )
        args, remaining_argv = config_parser.parse_known_args(argv)
        if args.conf_file:
            config = SafeConfigParser()
            config.readfp(args.conf_file)
            def_copy.update(dict(config.items('Defaults')))
        for key in def_copy.keys():
            env_key = '{}_{}'.format(env_prefix.upper(), key.upper())
            if os.getenv(env_key, False):
                def_copy[key] = os.getenv(env_key)
        parser.set_defaults(**def_copy)
        return parser.parse_args(remaining_argv)
# pylint: enable=too-few-public-methods
