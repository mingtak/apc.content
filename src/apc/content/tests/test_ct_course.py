# -*- coding: utf-8 -*-
from apc.content.content.course import ICourse  # NOQA E501
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


class CourseIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_course_schema(self):
        fti = queryUtility(IDexterityFTI, name='Course')
        schema = fti.lookupSchema()
        self.assertEqual(ICourse, schema)

    def test_ct_course_fti(self):
        fti = queryUtility(IDexterityFTI, name='Course')
        self.assertTrue(fti)

    def test_ct_course_factory(self):
        fti = queryUtility(IDexterityFTI, name='Course')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ICourse.providedBy(obj),
            u'ICourse not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_course_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Course',
            id='course',
        )
        self.assertTrue(
            ICourse.providedBy(obj),
            u'ICourse not provided by {0}!'.format(
                obj.id,
            ),
        )
