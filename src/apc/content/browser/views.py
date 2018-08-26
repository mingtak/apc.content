# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.PloneBatch import Batch
from Acquisition import aq_inner
import logging
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from email.mime.text import MIMEText
from plone.app.textfield.value import RichTextValue
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from collections import OrderedDict
import requests
import datetime

logger = logging.getLogger("apc.content")


class LiveClassView(BrowserView):
    """ Live Class View """
    template = ViewPageTemplateFile("template/live_class_view.pt")

    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        return self.template()


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
{'劉金花_5-4':[學生數, 開課級別, 開課語言, [校名, 語言, 等級, 人數], [校名, 語言, 等級, 人數],...],

....
}
"""
class MatchResult(BrowserView):
    """ Match Result """
    template = ViewPageTemplateFile("template/match_result.pt")

    def classroomIn(self, key):
        """ 決定開課學校 """
        courseTable = self.courseTable[key][3:]
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
                    #print '%s_%s' % (teacher.title, cTime)
                    # 開課時間吻合，開課語系吻合，開課程度吻合，共學校數未滿，最大學生數未滿，則成立
                    if self.courseTable.has_key('%s_%s' % (teacher.title, cTime)) and \
                       self.courseTable['%s_%s' % (teacher.title, cTime)][2] in ['', language] and \
                       self.courseTable['%s_%s' % (teacher.title, cTime)][1] in ['', level] and \
                       len(self.courseTable['%s_%s' % (teacher.title, cTime)]) < self.max_sc+2 and \
                       self.courseTable['%s_%s' % (teacher.title, cTime)][0] < self.max_st:

                        # 檢查是否已在其它時段開課
                        already = False
                        for item in self.courseTable:
                            if [school.title, language, level, int(req_lv)] in self.courseTable[item]:
                                #print '已開'
                                already = True
                                break
                        if not already:
                            # 加入共學，加計人數，確認語言，確認程度
                            self.courseTable['%s_%s' % (teacher.title, cTime)].append([school.title, language, level, int(req_lv)])
                            self.courseTable['%s_%s' % (teacher.title, cTime)][0] += int(req_lv)
                            self.courseTable['%s_%s' % (teacher.title, cTime)][1] = level
                            self.courseTable['%s_%s' % (teacher.title, cTime)][2] = language
                except:pass
                    #print '有錯'
#                    import pdb; pdb.set_trace()


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
                self.courseTable['%s_%s' % (teacher.title, item)] = [0, '', '']


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

        # 統計
#        self.result = {''}
#        for item in self.courseMatch:

        return self.template()


class PrepareLessons(BrowserView):
    template = ViewPageTemplateFile("template/prepare_lessons.pt")
    template_timesup = ViewPageTemplateFile("template/prepare_lessons_not_effective.pt")
    def __call__(self):
        request = self.request
        hashSHA256 = request.form.get('id', '')
        course = api.content.find(hashSHA256=hashSHA256)
        if len(course) == 1:
            self.course = course[0]
            current_time = datetime.datetime.now().date()
            if self.course.getObject().link_date > current_time:
                prepareUIDList = [item.UID for item in self.getPrepare()]
                if request.form.has_key('file-upload-widget'):
                    course_outline = request.get('course_outline', '')
                    if course_outline:
                        alsoProvides(self.request, IDisableCSRFProtection)
                        self.course.getObject().course_outline = RichTextValue(course_outline)
                    for uid in prepareUIDList:
                        upload_file = request.form['file-'+uid]
                        file_data =  upload_file.read()
                        if file_data:
                            item = api.content.get(UID=uid)
                            url = item.absolute_url()
                            headers = {
                                'Accept': "application/json",
                                'Content-Type': "application/json",
                                'Authorization': "Basic YWRtaW46MTIzNDU2",
                            }
                            data = {
                                "file": {
                                    "content-type": upload_file.headers['content-type'],
                                    "filename": upload_file.filename,
                                    "encoding": "base64",
                                    "data": file_data.encode('base64')
                                }
                            }
                            response = requests.request("PATCH", url, headers=headers, json=data)
                    self.request.response.redirect(self.request.URL)
                return self.template()
            else:
                return self.template_timesup()

    def getCourse(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
        return course

    def getPrepare(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
        prepare = api.content.find(context=course, portal_type="Prepare")
        return prepare


class CoursePrepare(BrowserView):
    template = ViewPageTemplateFile("template/course_prepare.pt")
    def __call__(self):
        request = self.request
        hashSHA256 = request.form.get('id', '')        
        course = api.content.find(hashSHA256=hashSHA256)
        if len(course) == 1:
            self.sendPrepareLessonsMail(course[0])

        return self.template()
    
    def getCourse(self):
        courses = api.content.find(portal_type="Course")
        return courses

    def sendPrepareLessonsMail(self, course):
        teacherObj = course.getObject().teacher.to_object
        teacher = teacherObj.title
        #t_mail  = teacherObj.email
        hashSHA256 = course.hashSHA256
        link = self.context.portal_url() + '/prepare_lessons?id=' + hashSHA256

        current_time = datetime.datetime.now().date()
        effective_date = current_time + datetime.timedelta(days=3)

        body_str = """ 您好 %s 老師: \
                  <br>  \
                  <br> 點擊以下連結可以上傳您課堂上的教材↓ \
                  <br> 此連結有效時間為 %s 請在時間內上傳完成\
                  <br> <a href="%s">%s</a> \
                  <br>  \
                  <br> 原住民族委員會 \
                   """ %(teacher.encode('utf8'), effective_date, link, link)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        teacher_email = teacherObj.email
        if teacher_email:
            api.portal.send_email(
                recipient=teacher_email,
                sender="service@apc.com.tw",
                subject="備課教材" ,
                body=mime_text.as_string(),
            )
            alsoProvides(self.request, IDisableCSRFProtection)
            course.getObject().link_date = effective_date
            
            self.context.plone_utils.addPortalMessage(_(u'It is success mail to ') + teacher, 'info')
        else:
            self.context.plone_utils.addPortalMessage(_(u'This teacher has not email: ') + teacher, 'info')


class PloneRootView(BrowserView):
    pass

class CourseView(BrowserView):
    pass


class TeacherView(BrowserView):
    def getTeacherField(self, item):
        fields = ['localLang'     , 'certification', 'study'     , 'qualified_teacher', \
                  'ethnic_teacher', 'education'    , 'experience', 'teaching_years'   , 'remarks'] 
        fieldsName = {'localLang' : _(u'Local Language')         , 'certification'    : _(u'Ethnic language certification'), 
                      'study'     : _(u'Revitalization study')   , 'qualified_teacher': _(u'Teaching class (Qualified teacher)'), 
                      'ethnic_teacher': _(u'Teaching class (Ethnic teacher)'), 'education'      : _(u'Education'),
                      'experience'    : _(u'work experience')                , 'teaching_years' : _(u'Teaching years'),
                      'remarks'       : _(u'Remarks')} 
        fieldsDict = OrderedDict()
        for field in fields:
            field_value = getattr(item, field, '')
            if field_value:
                fieldsDict.update({fieldsName[field]: field_value})
        if fieldsDict.has_key(fieldsName['localLang']):
            localLangValue = '\r\n'.join([lang.split(',')[1] for lang in fieldsDict[fieldsName['localLang']].split('/')])
            fieldsDict[fieldsName['localLang']] = localLangValue
        return fieldsDict


class TeacherListingView(FolderView):
    @property
    def b_size(self):
        b_size = getattr(self.request, 'b_size', None)\
            or getattr(self.request, 'limit_display', None) or 10
        return b_size

    @property
    def sort_on(self):
        sort_on = getattr(self.request, 'sort_on', 'getObjPositionInParent')
        return sort_on

    def getTeacherField(self, item):
        fields = ['localLang'     , 'certification', 'study'     , 'qualified_teacher', \
                  'ethnic_teacher', 'education'    , 'experience', 'teaching_years'   , 'remarks'] 
        fieldsName = {'localLang' : _(u'Local Language')         , 'certification'    : _(u'Ethnic language certification'), 
                      'study'     : _(u'Revitalization study')   , 'qualified_teacher': _(u'Teaching class (Qualified teacher)'), 
                      'ethnic_teacher': _(u'Teaching class (Ethnic teacher)'), 'education'      : _(u'Education'),
                      'experience'    : _(u'work experience')                , 'teaching_years' : _(u'Teaching years'),
                      'remarks'       : _(u'Remarks')} 
        fieldsDict = OrderedDict()
        for field in fields:
            field_value = getattr(item.getObject(), field, '')
            if field_value:
                fieldsDict.update({fieldsName[field]: field_value})
        if fieldsDict.has_key(fieldsName['localLang']):
            localLangValue = '\r\n'.join([lang.split(',')[1] for lang in fieldsDict[fieldsName['localLang']].split('/')])
            fieldsDict[fieldsName['localLang']] = localLangValue
        return fieldsDict

    def results(self, **kwargs):
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'Teacher')
        kwargs.setdefault('batch', True)
        kwargs.setdefault('sort_on', self.sort_on)

        listing = aq_inner(self.context).restrictedTraverse(
            '@@folderListing', None)
        results = listing(**kwargs)
        return results


class CourseListingView(FolderView):
    @property
    def b_size(self):
        b_size = getattr(self.request, 'b_size', None)\
            or getattr(self.request, 'limit_display', None) or 10
        return b_size

    @property
    def sort_on(self):
        sort_on = getattr(self.request, 'sort_on', 'getObjPositionInParent')
        return sort_on

    def getPrepare(self, obj):
        prepare = api.content.find(context=obj, portal_type="Prepare")
        return prepare

    def results(self, **kwargs):
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'Course')
        kwargs.setdefault('batch', True)
        kwargs.setdefault('sort_on', self.sort_on)

        listing = aq_inner(self.context).restrictedTraverse(
            '@@folderListing', None)
        results = listing(**kwargs)
        return results

