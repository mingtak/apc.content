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


class ISchool(model.Schema):
    """ Marker interface and Dexterity Python Schema for School
    """

    email = schema.TextLine(
        title=_(u'Email'),
        required=False
    )

    seed = schema.Bool(
        title=_(u'Seed School'),
        default=False,
        required=False
    )

    fieldset(_(u'School ID PW'), fields=['school_id', 'school_pw'])
    school_id = schema.TextLine(
        title=_(u'School Login Id'),
        required=False,
    )

    school_pw = schema.TextLine(
        title=_(u'School Password'),
        required=False,
    )

    # directives.widget(level=RadioFieldWidget)
    # level = schema.Choice(
    #     title=_(u'Sponsoring Level'),
    #     vocabulary=LevelVocabulary,
    #     required=True
    # )

    # text = RichText(
    #     title=_(u'Text'),
    #     required=False
    # )

    # url = schema.URI(
    #     title=_(u'Link'),
    #     required=False
    # )

    # fieldset('Images', fields=['logo', 'advertisement'])
    # logo = namedfile.NamedBlobImage(
    #     title=_(u'Logo'),
    #     required=False,
    # )

    # advertisement = namedfile.NamedBlobImage(
    #     title=_(u'Advertisement (Gold-sponsors and above)'),
    #     required=False,
    # )

    # directives.read_permission(notes='cmf.ManagePortal')
    # directives.write_permission(notes='cmf.ManagePortal')
    # notes = RichText(
    #     title=_(u'Secret Notes (only for site-admins)'),
    #     required=False
    # )


@implementer(ISchool)
class School(Item):
    """
    """
