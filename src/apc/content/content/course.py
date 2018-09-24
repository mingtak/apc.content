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
    vMeetingRoom = schema.TextLine(
        title=_(u'Virtual Meeting Room'),
        required=False,
    )

    local_language = schema.TextLine(
        title=_(u'Local Language'),
        required=False,
    )

    teacher = RelationChoice(
        title=_(u'Teacher'),
        source=CatalogSource(portal_type='Teacher'),
        required=False,
    )

    school = RelationList(
        title=_(u'Alliance Schools'),
        value_type=RelationChoice(
                     title=u"School",
                     source=CatalogSource(
                         portal_type=['School', 'Folder'])
        ),
        required=False,
    )

    hire_school = RelationChoice(
        title=_(u'Hire School'),
        source=CatalogSource(portal_type=['School', 'Folder']),
        required=False,
    )

    studentList = schema.Text(
        title=_(u'Student List'),
        description=_(u'format: city,school_name,student_name'),
        required=False,
    )

    place = schema.TextLine(
        title=_(u'Place of Study'),
        required=False,
    )

    course_date = schema.TextLine(
        title=_(u'Course Date'),
        required=False,
    )

    course_time = schema.TextLine(
        title=_(u'Course Time'),
        required=False,
    )

    course_outline = RichText(
        title=_(u'Course Outline'),
        required=False,
    )


@implementer(ICourse)
class Course(Container):
    """
    """
