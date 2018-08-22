# -*- coding: utf-8 -*-
from apc.content.content.prepare import IPrepare  # NOQA E501
from apc.content.testing import APC_CONTENT_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class PrepareIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_prepare_schema(self):
        fti = queryUtility(IDexterityFTI, name='Prepare')
        schema = fti.lookupSchema()
        self.assertEqual(IPrepare, schema)

    def test_ct_prepare_fti(self):
        fti = queryUtility(IDexterityFTI, name='Prepare')
        self.assertTrue(fti)

    def test_ct_prepare_factory(self):
        fti = queryUtility(IDexterityFTI, name='Prepare')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPrepare.providedBy(obj),
            u'IPrepare not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_prepare_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Prepare',
            id='prepare',
        )
        self.assertTrue(
            IPrepare.providedBy(obj),
            u'IPrepare not provided by {0}!'.format(
                obj.id,
            ),
        )
