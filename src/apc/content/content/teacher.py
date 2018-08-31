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


class ITeacher(model.Schema):

    fieldset(_('Teacher Info'), fields=['image', 'certification', 'study', 'qualified_teacher', 'ethnic_teacher', 'education', 'experience', 'teaching_years', 'remarks'])

    image = namedfile.NamedBlobImage(
        title=_(u'Teacher Image'),
        required=False,
    )

    certification = schema.Text(
        title=_(u"Ethnic language certification"),
        required=False
    )

    study = schema.Text(
        title=_(u"Revitalization study"),
        required=False
    )

    qualified_teacher = schema.Text(
        title=_(u"Teaching class (Qualified teacher)"),
        required=False
    )

    ethnic_teacher = schema.Text(
        title=_(u"Teaching class (Ethnic teacher)"),
        required=False
    )

    education = schema.Text(
        title=_(u"Education"),
        required=False
    )

    experience = schema.Text(
        title=_(u"work experience"),
        required=False
    )

    teaching_years = schema.Text(
        title=_(u"Teaching years"),
        required=False
    )

    remarks = schema.Text(
        title=_(u"Remarks"),
        required=False
    )

    email = schema.TextLine(
        title=_(u"Email"),
        required=False
    )

    fieldset(_(u'Link Effective Date'), fields=['link_date'])
    link_date = schema.Date(
        title=_(u'Prepare Lessons Link Effective Date'),
        required=False,
    )

    fieldset(_(u'Teacher ID PW'), fields=['teacher_id', 'teacher_pw'])
    teacher_id = schema.TextLine(
        title=_(u'Teacher Username'),
        required=False,
    )

    teacher_pw = schema.TextLine(
        title=_(u'Teacher Password'),
        required=False,
    )


@implementer(ITeacher)
class Teacher(Item):
    """
    """
   
