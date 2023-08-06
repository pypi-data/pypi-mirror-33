#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from nti.testing.layers import find_test
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin

import zope.testing.cleanup

class ContentfragmentsTestLayer(ZopeComponentLayer, ConfiguringLayerMixin):

    set_up_packages = ('nti.contentfragments',)

    @classmethod
    def setUp(cls):
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        zope.testing.cleanup.cleanUp()

    @classmethod
    def testSetUp(cls, test=None):
        pass

    @classmethod
    def testTearDown(cls):
        pass

import unittest

class ContentfragmentsLayerTest(unittest.TestCase):
    layer = ContentfragmentsTestLayer
