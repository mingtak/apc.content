# -*- coding: utf-8 -*-

from apc.content import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IOptional(model.Schema):
    """
    """

    language = schema.List(
        title=_(u'Language'),
        value_type=schema.Choice(
            title=_(u"Language"),
            vocabulary='apc.content.Language',
            required=False,
        ),
        required=True
    )

    classTime = schema.List(
        title=_(u'Class Time'),
        value_type=schema.Choice(
            title=_(u"Class Time"),
            vocabulary='apc.content.ClassTime',
            required=False,
        ),
        required=True
    )

@implementer(IOptional)
@adapter(IDexterityContent)
class Optional(object):
    def __init__(self, context):
        self.context = context

    @property
    def project(self):
        if hasattr(self.context, 'project'):
            return self.context.project
        return None

    @project.setter
    def project(self, value):
        self.context.project = value
