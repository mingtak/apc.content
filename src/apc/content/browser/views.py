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

        teachers = portal['teacher'].getChildNodes()
        schools = portal['school'].getChildNodes()

        # 確認可開班狀況
        courseTable = {}
        for teacher in teachers:
            for item in teacher.classTime:
                courseTable['%s_%s' % (teacher.title, item)] = [0]


        for teacher in teachers:
            # 老師能教
            canTeach = {}
            for item in teacher.localLang.split('/'):
                language = ''.join(item.split(',')[0:2])
                canTeach[language] = item

            for school in schools:
                if school.classTime is None:
                    continue

                # 學校需要
                reqLang = []
                if school.localLang is None:
                    continue
                for item in school.localLang.split('/'):
                    # 逐個語言比對
                    language = ''.join(item.split(',')[0:2])
                    if language in canTeach.keys():
                        req_lv_1, req_lv_2, req_lv_3 = item.split(',')[2:]
                        can_lv_1, can_lv_2, can_lv_3 = canTeach[language].split(',')[2:]
                        # 比對等級/人數
                        if int(can_lv_1) and int(req_lv_1):
                            for cTime in school.classTime:
                                try:
                                    print '%s_%s' % (teacher.title, cTime)
                                    if courseTable.has_key('%s_%s' % (teacher.title, cTime)) and \
                                       courseTable['%s_%s' % (teacher.title, cTime)][0] < 10:    # TODO: 寫死學生數
                                        courseTable['%s_%s' % (teacher.title, cTime)].append([school.title, language, 'primary', int(req_lv_1)])
                                        courseTable['%s_%s' % (teacher.title, cTime)][0] += int(req_lv_1)
                                except:
                                    print '有錯'
                                    import pdb; pdb.set_trace()


#中階
                        if int(can_lv_2) and int(req_lv_2):
                            for cTime in school.classTime:
                                try:
                                    print '%s_%s' % (teacher.title, cTime)
                                    if courseTable.has_key('%s_%s' % (teacher.title, cTime)) and \
                                       courseTable['%s_%s' % (teacher.title, cTime)][0] < 10:    # TODO: 寫死學生數
                                        courseTable['%s_%s' % (teacher.title, cTime)].append([school.title, language, 'intermediate', int(req_lv_2)])
                                        courseTable['%s_%s' % (teacher.title, cTime)][0] += int(req_lv_2)
                                except:
                                    print '有錯'
                                    import pdb; pdb.set_trace()

#高階
                        if int(can_lv_3) and int(req_lv_3):
                            for cTime in school.classTime:
                                try:
                                    print '%s_%s' % (teacher.title, cTime)
                                    if courseTable.has_key('%s_%s' % (teacher.title, cTime)) and \
                                       courseTable['%s_%s' % (teacher.title, cTime)][0] < 10:    # TODO: 寫死學生數
                                        courseTable['%s_%s' % (teacher.title, cTime)].append([school.title, language, 'advanced', int(req_lv_3)])
                                        courseTable['%s_%s' % (teacher.title, cTime)][0] += int(req_lv_3)
                                except:
                                    print '有錯'
                                    import pdb; pdb.set_trace()


        self.courseTable = courseTable
#        import pdb; pdb.set_trace()
        return self.template()
