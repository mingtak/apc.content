# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from apc.content import _


class IPrepare(model.Schema):

    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    topic = schema.TextLine(
        title=_(u'Prepare Theme'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Prepare Description'),
        required=False,
    )

    file = namedfile.NamedBlobFile(
        title=_(u'Teaching material'),
        required=False,
    )

    file2 = namedfile.NamedBlobFile(
        title=_(u'Teaching material'),
        required=False,
    )

    file3 = namedfile.NamedBlobFile(
        title=_(u'Teaching material'),
        required=False,
    )

    vacation = schema.Bool(
        title=_(u'vacation'),
        default=False,
        required=True
    )

    """ 
    video = RichText(
        title=_(u'Course Video'),
        required=False,
    ) """

    embeded = schema.Text(
        title=_(u'Embeded Code'),
        required=False,
    )

    onCall = schema.Text(
        title=_(u'Roll Call, On Call'),
        required=False,
    )

    notOnCall = schema.Text(
        title=_(u'Roll Call, Not On Call'),
        required=False,
    )

    fieldset(_(u'Leave a Lesson'), fields=['leave', 'makeUp', 'makeUpDay'])
    leave = schema.Text(
        title=_(u'Leave a Lesson'),
        required=False,
    )

    makeUp = schema.Bool(
        title=_(u'Make up a missed lesson'),
        required=False,
    )

    makeUpDay = schema.TextLine(
        title=_(u'Make Up Day'),
        required=False,
    )

@implementer(IPrepare)
class Prepare(Item):
    """
    """
