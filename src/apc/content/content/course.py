# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.interface import implementer
from apc.content import _


class ICourse(model.Schema):

    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    teacher = RelationChoice(
        title=_(u'Teacher'),
        source=CatalogSource(portal_type='Teacher'),
        required=False,
    )

    school = RelationList(
        title=_(u'Schools'),
        value_type=RelationChoice(
                     title=u"School",
                     source=CatalogSource(
                         portal_type='School')
        ),
        required=False,
    )


@implementer(ICourse)
class Course(Container):
    """
    """
