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


""" 範例:
{'劉金花_5-4':[學生數, 開課級別, [校名, 語言, 等級, 人數], [校名, 語言, 等級, 人數],...],

....
}
"""
class MatchResult(BrowserView):
    """ Match Result """
    template = ViewPageTemplateFile("template/match_result.pt")

    def classroomIn(self, key):
        """ 決定開課學校 """
        courseTable = self.courseTable[key][2:]
        classroom = ''
        for index in range(len(courseTable)):
            if classroom == '':
                classroom = courseTable[index][0]
            elif int(courseTable[index][-1]) > int(courseTable[index-1][-1]):
                classroom =courseTable[index][0]
        return classroom


    def courseMatch(self, language, level, can_lv, req_lv, school, teacher):
        """ 比對等級/人數 """
        if int(can_lv) and int(req_lv):
            for cTime in school.classTime:
                try:
                    print '%s_%s' % (teacher.title, cTime)
                    if self.courseTable.has_key('%s_%s' % (teacher.title, cTime)) and \
                       self.courseTable['%s_%s' % (teacher.title, cTime)][1] in ['', level] and \
                       len(self.courseTable['%s_%s' % (teacher.title, cTime)]) < self.max_sc+2 and \
                       self.courseTable['%s_%s' % (teacher.title, cTime)][0] < self.max_st:

                        # 檢查是否已在其它時段開課
                        already = False
                        for item in self.courseTable:
                            if [school.title, language, level, int(req_lv)] in self.courseTable[item]:
                                print '已開'
                                already = True
                                break
                        if not already:
                            self.courseTable['%s_%s' % (teacher.title, cTime)].append([school.title, language, level, int(req_lv)])
                            self.courseTable['%s_%s' % (teacher.title, cTime)][0] += int(req_lv)
                            self.courseTable['%s_%s' % (teacher.title, cTime)][1] = level
                except:
                    print '有錯'
                    import pdb; pdb.set_trace()


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        # min costudy schools(min_sc)
        self.min_sc=int(request.form.get('min_sc', 3))

        # max costudy schools(max_sc) and students(max_st) limit
        self.max_sc=int(request.form.get('max_sc', 6))
        self.max_st=int(request.form.get('max_st', 10))

        factory1 = getUtility(IVocabularyFactory, 'apc.content.ClassTime')
        self.vocaClassTime = factory1(context)

        teachers = portal['teacher'].getChildNodes()
        schools = portal['school'].getChildNodes()

        # 確認可開班狀況
        self.courseTable = {}
        for teacher in teachers:
            for item in teacher.classTime:
                # [學生數, 開課級別]
                self.courseTable['%s_%s' % (teacher.title, item)] = [0, '']


        for teacher in teachers:
            # 老師能教
            canTeach = {}
            for item in teacher.localLang.split('/'):
                language = item.split(',')[1]
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
                    language = item.split(',')[1]

                    if language in canTeach.keys():
                        req_lv_1, req_lv_2, req_lv_3 = item.split(',')[2:]
                        can_lv_1, can_lv_2, can_lv_3 = canTeach[language].split(',')[2:]

                        self.courseMatch(language, 'primary', can_lv_1, req_lv_1, school, teacher)
                        self.courseMatch(language, 'intermediate', can_lv_2, req_lv_2, school, teacher)
                        self.courseMatch(language, 'advanced', can_lv_3, req_lv_3, school, teacher)

        return self.template()
