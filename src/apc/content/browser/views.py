# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.PloneBatch import Batch
from Acquisition import aq_inner
import logging
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

logger = logging.getLogger("apc.content")


class SchoolOverview(BrowserView):
    """ School Overview """
    template = ViewPageTemplateFile("template/school_overview.pt")

    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        factory = getUtility(IVocabularyFactory, 'apc.content.ClassTime')
        self.vocaClassTime = factory(context)

        return self.template()


class MatchResult(BrowserView):
    """ Match Result """
    template = ViewPageTemplateFile("template/match_result.pt")

    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        factory1 = getUtility(IVocabularyFactory, 'apc.content.ClassTime')
        self.vocaClassTime = factory1(context)
        factory2 = getUtility(IVocabularyFactory, 'apc.content.Language')
        self.vocaLanguage = factory2(context)

        teachers = context['teachers'].getChildNodes()
        schools = context['schools'].getChildNodes()

        self.matchs = {}
        scount = 0
        for school in schools:
            sLanguage = school.language
            sClassTime = school.classTime
            self.matchs[school.title] = []
            tcount = 0
            for teacher in teachers:
#                print 'LOOP: %s, %s' % (scount , tcount)
                tLanguage = teacher.language
                tClassTime = teacher.classTime
#                self.matchs[school.title] = []
                if set(tClassTime).intersection(sClassTime) and set(tLanguage).intersection(sLanguage):
                    self.matchs[school.title].append(
                        [teacher.title,
                         list(set(tClassTime).intersection(sClassTime)),
                         list(set(tLanguage).intersection(sLanguage))
                        ]
                    )
#                    print 'MATCH: %s, %s' % (scount, tcount)
#                    import pdb; pdb.set_trace()
                tcount += 1
            scount += 1
#        import pdb; pdb.set_trace()

        return self.template()
