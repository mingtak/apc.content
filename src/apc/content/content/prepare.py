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

    description = schema.Text(
        title=_(u'Agenda'),
        required=False,
    )

    file = namedfile.NamedFile(
        title=_(u'Teaching material'),
        required=False,
    )

    video = RichText(
        title=_(u'Course Video'),
        required=False,
    )


@implementer(IPrepare)
class Prepare(Item):
    """
    """
