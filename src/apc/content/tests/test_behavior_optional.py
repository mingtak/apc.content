# -*- coding: utf-8 -*-
from apc.content.behaviors.optional import IOptional
from apc.content.testing import APC_CONTENT_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class OptionalIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_optional(self):
        behavior = getUtility(IBehavior, 'apc.content.optional')
        self.assertEqual(
            behavior.marker,
            IOptional,
        )
        behavior_name = 'apc.content.behaviors.optional.IOptional'
        behavior = getUtility(IBehavior, behavior_name)
        self.assertEqual(
            behavior.marker,
            IOptional,
        )
