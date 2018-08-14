# -*- coding: utf-8 -*-
from apc.content.content.live_class import ILiveClass  # NOQA E501
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


class LiveClassIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Folder',
            self.portal,
            'live_class',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_live_class_schema(self):
        fti = queryUtility(IDexterityFTI, name='LiveClass')
        schema = fti.lookupSchema()
        self.assertEqual(ILiveClass, schema)

    def test_ct_live_class_fti(self):
        fti = queryUtility(IDexterityFTI, name='LiveClass')
        self.assertTrue(fti)

    def test_ct_live_class_factory(self):
        fti = queryUtility(IDexterityFTI, name='LiveClass')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILiveClass.providedBy(obj),
            u'ILiveClass not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_live_class_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='LiveClass',
            id='live_class',
        )

        self.assertTrue(
            ILiveClass.providedBy(obj),
            u'ILiveClass not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_live_class_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='LiveClass')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
