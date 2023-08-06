#!/usr/bin/env python

from __future__ import absolute_import
__version__ = "$Revision: 1.2 $"

from autolog import autolog
import unittest

LOG = autolog()

LOG.error("error test")

if __name__ == "__main__":
    unittest.main()
