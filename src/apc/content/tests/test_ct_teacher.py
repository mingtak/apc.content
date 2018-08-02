# -*- coding: utf-8 -*-
from apc.content.content.teacher import ITeacher  # NOQA E501
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


class TeacherIntegrationTest(unittest.TestCase):

    layer = APC_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_teacher_schema(self):
        fti = queryUtility(IDexterityFTI, name='Teacher')
        schema = fti.lookupSchema()
        self.assertEqual(ITeacher, schema)

    def test_ct_teacher_fti(self):
        fti = queryUtility(IDexterityFTI, name='Teacher')
        self.assertTrue(fti)

    def test_ct_teacher_factory(self):
        fti = queryUtility(IDexterityFTI, name='Teacher')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ITeacher.providedBy(obj),
            u'ITeacher not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_teacher_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Teacher',
            id='teacher',
        )

        self.assertTrue(
            ITeacher.providedBy(obj),
            u'ITeacher not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_teacher_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Teacher')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
