# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.interface import implementer
from apc.content import _


class IStudent(model.Schema):

    studentId = schema.TextLine(
        title=_(u"Student Id"),
        required=False
    )

    birthday = schema.Date(
        title=_(u"Birthday"),
        required=False
    )

    address = schema.TextLine(
        title=_(u"Address"),
        required=False
    )

    course = RelationChoice(
        title=_(u'Learning Course'),
        source=CatalogSource(po2rtal_type=['Course', 'Folder']),
        required=False,
    )

    fieldset(_(u'Student ID PW'), fields=['student_id', 'student_pw'])
    student_id = schema.TextLine(
        title=_(u'Student Username'),
        required=False,
    )

    student_pw = schema.TextLine(
        title=_(u'Student Password'),
        required=False,
    )


@implementer(IStudent)
class Student(Item):
    """
    """
