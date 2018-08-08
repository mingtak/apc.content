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

    localLang = schema.TextLine(
        title=_(u'Local Language'),
        description=_(u'Format example: D20,Language Name,1,1,1/A01,Language Name,0,1,3/..., 0,0,0 or 0,1,3 mapping to primary-intermediate-advanced'),
        required=True,
    )

    classTime = schema.List(
        title=_(u'Class Time'),
        value_type=schema.Choice(
            title=_(u"Class Time"),
            vocabulary='apc.content.ClassTime',
            required=False,
        ),
        required=False
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
