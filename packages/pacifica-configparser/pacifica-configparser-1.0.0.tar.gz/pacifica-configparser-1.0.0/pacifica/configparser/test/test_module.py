#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the module."""
from unittest import TestCase


class TestModule(TestCase):
    """Test the module main imports."""

    def test_module(self):
        """Import the module see if it works."""
        hit_exception = False
        try:
            import pacifica.configparser
            self.assertTrue(pacifica.configparser)
        except ImportError:  # pragma: no cover good run shouldn't get here
            hit_exception = True
        self.assertFalse(hit_exception)
