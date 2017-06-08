#!/usr/bin/env python

import unittest
from dinghy import Dinghy

class TestDinghy(unittest.TestCase):
    """
    Tests for `dinghy.py`
    """

    def test_instantiating(self):
        """ Test that Dinghy class can be instantiated """
        dinghy = Dinghy(show_progress=True)
