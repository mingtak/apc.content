# -*- coding: utf-8 -*-
from apc.content.content.school import ISchool  # NOQA E501
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


class SchoolIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_school_schema(self):
        fti = queryUtility(IDexterityFTI, name='School')
        schema = fti.lookupSchema()
        self.assertEqual(ISchool, schema)

    def test_ct_school_fti(self):
        fti = queryUtility(IDexterityFTI, name='School')
        self.assertTrue(fti)

    def test_ct_school_factory(self):
        fti = queryUtility(IDexterityFTI, name='School')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ISchool.providedBy(obj),
            u'ISchool not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_school_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='School',
            id='school',
        )

        self.assertTrue(
            ISchool.providedBy(obj),
            u'ISchool not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_school_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='School')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
