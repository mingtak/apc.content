# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection


class AnnouncementViewlet(base.ViewletBase):
    pass


class ThreeIconViewlet(base.ViewletBase):
    pass


