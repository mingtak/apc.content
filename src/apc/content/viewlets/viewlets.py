# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from mingtak.ECBase.browser.views import SqlObj


class AnnouncementViewlet(base.ViewletBase):
    pass


class ThreeIconViewlet(base.ViewletBase):
    pass


class ActiveHighlightsViewlet(base.ViewletBase):
    pass


class PageCountViewlet(base.ViewletBase):
    def update(self):
        execSql = SqlObj()
        url = self.context.absolute_url()
        try:
            title = self.context.title.encode('utf-8')
        except:
            title = self.context.title

        sqlStr = """INSERT INTO page_count(url, title, count) VALUES('{}', '{}', 1) ON DUPLICATE KEY UPDATE count = count + 1,
                    title = '{}'""".format(url, title, title)
        execSql.execSql(sqlStr)
