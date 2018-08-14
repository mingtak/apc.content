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
from z3c.relationfield.schema import RelationList, RelationChoice
from plone.app.vocabularies.catalog import CatalogSource
from apc.content import _


class ILiveClass(model.Schema):
    """ Marker interface and Dexterity Python Schema for LiveClass
    """

    localLang = schema.TextLine(
        title=_(u'Local Language'),
        required=True,
    )

    teachSchool = RelationChoice(
        title=_(u"Teach School"),
        required=True,
        source=CatalogSource(Type='School')
    )

    coSchool = RelationList(
        title=_(u"Training Center"),
        default=[],
        value_type=RelationChoice(title=_(u"Related"),
            source=CatalogSource(Type='School')
        ),
        required=False,
    )

    teacher = RelationChoice(
        title=_(u"Teacher"),
        required=True,
        source=CatalogSource(Type='Teacher')
    )

    embeded = schema.Text(
        title=_(u'Embeded Code'),
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


@implementer(ILiveClass)
class LiveClass(Item):
    """
    """
