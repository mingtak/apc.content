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
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from email.mime.text import MIMEText
from plone.app.textfield.value import RichTextValue
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from collections import OrderedDict
from collections import defaultdict
import requests
import datetime
import hashlib
from DateTime import DateTime

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


class MatchSystem(BrowserView):
    """ Match System """
    template = ViewPageTemplateFile("template/match_system.pt")

    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        isAnon = api.user.is_anonymous()
        if isAnon:
            return request.response.redirect(self.portal.absolute_url())
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
                    #print '%s_%s' % (school.title, cTime)
                    # 開課時間吻合，開課語系吻合，開課程度吻合，共學校數未滿，最大學生數未滿，則成立
                    if self.courseTable.has_key('%s_%s' % (school.title, cTime)) and \
                       self.courseTable['%s_%s' % (school.title, cTime)][2] in ['', language] and \
                       self.courseTable['%s_%s' % (school.title, cTime)][1] in ['', level] and \
                       len(self.courseTable['%s_%s' % (school.title, cTime)]) < self.max_sc+2 and \
                       self.courseTable['%s_%s' % (school.title, cTime)][0] < self.max_st:

                        # 檢查是否已在其它時段開課
                        already = False
                        for item in self.courseTable:
                            if [school.title, language, level, int(req_lv)] in self.courseTable[item]:
                                #print '已開'
                                already = True
                                break
                        if not already:
                            # 加入共學，加計人數，確認語言，確認程度
                            self.courseTable['%s_%s' % (school.title, cTime)].append([school.title, language, level, int(req_lv)])
                            self.courseTable['%s_%s' % (school.title, cTime)][0] += int(req_lv)
                            self.courseTable['%s_%s' % (school.title, cTime)][1] = level
                            self.courseTable['%s_%s' % (school.title, cTime)][2] = language
                except:pass
                    #print '有錯'
#                    import pdb; pdb.set_trace()


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        isAnon = api.user.is_anonymous()
        if isAnon:
            return request.response.redirect(portal.absolute_url())

        # min costudy schools(min_sc)
        self.min_sc=int(request.form.get('min_sc', 3))
        # max costudy schools(max_sc) and students(max_st) limit
        self.max_sc=int(request.form.get('max_sc', 6))
        self.max_st=int(request.form.get('max_st', 10))

        factory1 = getUtility(IVocabularyFactory, 'apc.content.ClassTime')
        self.vocaClassTime = factory1(context)

        teachers = portal['teacher'].getChildNodes()
        schools = api.content.find(context=portal['school'], Type='School')

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

            for school_item in schools:
                school = school_item.getObject()
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
    def __call__(self):
        request = self.request
        courseUID = request.form.get('id', '')
        course = api.content.find(portal_type='Course', UID=courseUID, sort_on='getObjPositionInParent')
        if len(course) == 1:
            teacher_uid = self.request.cookies.get("teacher_login", "")
            teacher = api.content.get(UID=teacher_uid)
            if not teacher:
                return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
            self.teacher = teacher

            self.course = course[0]
            if self.course.course_teacher != self.teacher.UID():
                return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))

            prepareUIDList = [item.UID for item in self.getPrepare()]
            if request.form.has_key('file-upload-widget'):
                course_outline = request.get('course_outline', '')
                if course_outline:
                    alsoProvides(self.request, IDisableCSRFProtection)
                    self.course.getObject().course_outline = RichTextValue(course_outline)
                for uid in prepareUIDList:
                    item = api.content.get(UID=uid)
                    url = item.absolute_url()
                    upload_file = request.form['file-'+uid]
                    upload_text = request.form['text-'+uid]
                    headers = {
                        'Accept': "application/json",
                        'Content-Type': "application/json",
                        'Authorization': "Basic YWRtaW46MTIzNDU2",
                    }
                    data = {"description": upload_text}

                    file_data =  upload_file.read()
                    if file_data:
                        data.update(
                            { \
                                "file": { \
                                "content-type": upload_file.headers['content-type'], \
                                "filename": upload_file.filename, \
                                "encoding": "base64", \
                                "data": file_data.encode('base64') \
                                } \
                            } \
                        )
                    response = requests.request("PATCH", url, headers=headers, json=data)
                self.request.response.redirect(self.request.URL)
            return self.template()
        else:
            return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))

    def getCourse(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
        return course

    def getPrepare(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
#        import pdb ; pdb.set_trace()
        prepare = api.content.find(context=course, portal_type="Prepare",
                                   start={'query':DateTime(), 'range':'min'}, sort_on='getObjPositionInParent')
        return prepare


class PrepareUniLessons(BrowserView):
    template = ViewPageTemplateFile("template/prepare_uni_lessons.pt")
    def __call__(self):
        request = self.request
        prepareUID = request.form.get('id', '')
        prepare = api.content.find(portal_type='Prepare', UID=prepareUID, sort_on='getObjPositionInParent')
        if len(prepare) == 1:
            teacher_uid = self.request.cookies.get("teacher_login", "")
            teacher = api.content.get(UID=teacher_uid)
            if not teacher:
                return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
            self.teacher = teacher
            
            self.prepare = prepare[0]
            course_teacher = self.prepare.getObject().getParentNode().teacher.to_object.UID()
            if course_teacher != self.teacher.UID(): 
                return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))


            if request.form.has_key('file-upload-widget'):
                self.updatePrepare()
                self.request.response.redirect(self.request.URL)

            return self.template()
        else:
            return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))

    def updatePrepare(self):
        request = self.request
        upload_file = request.form.get('file', '')
        upload_text = request.form.get('text', '')

        url = self.prepare.getURL()
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'Authorization': "Basic YWRtaW46MTIzNDU2",
        }
        data = {"description": upload_text}

        file_data =  upload_file.read()
        if file_data:
            data.update(
                { \
                    "file": { \
                        "content-type": upload_file.headers['content-type'], \
                        "filename": upload_file.filename, \
                        "encoding": "base64", \
                        "data": file_data.encode('base64') \
                    } \
                } \
            )
        response = requests.request("PATCH", url, headers=headers, json=data)

class SendTeacherLink(BrowserView):
    template = ViewPageTemplateFile("template/send_teacher_link.pt")
    def __call__(self):
        request = self.request
        hashSHA256 = request.form.get('id', '')
        teacher = api.content.find(hashSHA256=hashSHA256)
        if len(teacher) == 1:
            self.sendTeacherInitMail(teacher[0])

        return self.template()
    
    def getCourseTeachers(self):
        courses = api.content.find(portal_type="Course", sort_on='getObjPositionInParent')
        teachers = defaultdict(list)
        for course in courses:
            if hasattr(course.getObject().teacher, 'to_object'):
                teacher = course.getObject().teacher.to_object
                teachers[teacher].append(course)
        return teachers

    def sendTeacherInitMail(self, teacher):
        teacher_title = teacher.Title
        hashSHA256 = teacher.hashSHA256
        link = self.context.portal_url() + '/teacher-area/teacher-login/@@teacher_init?id=' + hashSHA256

        current_time = datetime.datetime.now().date()
        effective_date = current_time + datetime.timedelta(days=3)

        body_str = """ 您好 %s 老師: \
                  <br>  \
                  <br> 點擊以下連結可以設定您的帳號密碼↓ \
                  <br> 此連結有效時間為 %s 請在時間內設定完成\
                  <br> <a href="%s">%s</a> \
                  <br>  \
                  <br> 原住民族委員會 \
                   """ %(teacher_title, effective_date, link, link)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        teacher_email = teacher.getObject().email
        if teacher_email:
            api.portal.send_email(
                recipient=teacher_email,
                sender="service@apc.com.tw",
                subject="備課教材" ,
                body=mime_text.as_string(),
            )
            alsoProvides(self.request, IDisableCSRFProtection)
            teacher.getObject().link_date = effective_date

            self.context.plone_utils.addPortalMessage(_(u'It is success mail to ') + teacher.Title.decode('utf8'), 'info')
        else:
            self.context.plone_utils.addPortalMessage(_(u'This teacher has not email: ') + teacher.Title.decode('utf8'), 'info')

    def getHashSHA256(self, uid):
        return hashlib.sha256(uid).hexdigest() 


class TeacherInit(BrowserView):
    template = ViewPageTemplateFile("template/teacher_init.pt")
    template_login = ViewPageTemplateFile("template/teacher_login.pt")
    def __call__(self):
        request = self.request
        hashSHA256 = request.form.get('id', '')
        teacher = api.content.find(hashSHA256=hashSHA256)

        if len(teacher) == 1:
            self.teacher = teacher[0]
        
        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            portal_catalog = getToolByName(self.context, 'portal_catalog')
            index_id = portal_catalog.Indexes['teacher_id']
            teacher_id = request.form.get('teacher_id', '')
            teacher_pw = request.form.get('teacher_pw', '')
            if request.form.get('widget-registered-btn', '') == 'widget-registered-btn':
                if teacher_id == self.teacher.teacher_id or teacher_id not in index_id.uniqueValues():
                    self.initTeacher(teacher_id, teacher_pw, hashSHA256)
                else: 
                    self.context.plone_utils.addPortalMessage(_(u'This Teacher ID is already be used'), 'error')
            else:
                self.checkLogin(teacher_id, teacher_pw)

        if len(teacher) != 1:
            return self.template_login()
        return self.template()

    def initTeacher(self, teacher_id, teacher_pw, hashSHA256):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.teacher.getObject().teacher_id = teacher_id
        self.teacher.getObject().teacher_pw = teacher_pw

        current_time = datetime.datetime.now().date()
        effective_date = current_time - datetime.timedelta(days=3)
        self.teacher.getObject().link_date = effective_date

        cookie_path = api.portal.get().absolute_url_path()
        self.request.response.setCookie("teacher_login", self.teacher.UID, path=cookie_path)
        self.teacher.getObject().reindexObject()

        return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url())) 

    def checkLogin(self, teacher_id, teacher_pw):
        teacher = api.content.find(portal_type='Teacher', teacher_id=teacher_id, sort_on='getObjPositionInParent')
        if len(teacher) == 1:
            if teacher[0].getObject().teacher_pw == teacher_pw:

                cookie_path = api.portal.get().absolute_url_path()
                self.request.response.setCookie("teacher_login", teacher[0].UID, path=cookie_path)

                return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))
 
        self.context.plone_utils.addPortalMessage(_(u'Your Username or Password is not vaild'), 'error')

    
class TeacherInfo(BrowserView):
    template = ViewPageTemplateFile("template/teacher_info.pt")
    def __call__(self):
        request = self.request
        teacher_uid = self.request.cookies.get("teacher_login", "")
        teacher = api.content.find(UID=teacher_uid, sort_on='getObjPositionInParent')
        if len(teacher) != 1:
            return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
        self.teacher = teacher[0]

        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            teacherFields = ['certification', 'study', 'qualified_teacher', 'ethnic_teacher', 'education', 'experience', 'teaching_years', 'remarks', 'email']
            data = {}
            url = self.teacher.getURL()
            headers = {
                'Accept': "application/json",
                'Content-Type': "application/json",
                'Authorization': "Basic YWRtaW46MTIzNDU2",
            }
            for field in teacherFields:
                value = request.form.get(field, '')
                if value: 
                    data.update({field: value})
            image = request.form.get('image', '')
            if image:
                data.update(
                    {
                        "image": {
                            "content-type": image.headers['content-type'],
                            "filename": image.filename,
                            "encoding": "base64",
                            "data": image.read().encode('base64')
                        }
                    }
                )
         
            response = requests.request("PATCH", url, headers=headers, json=data)
            self.context.plone_utils.addPortalMessage(_(u'The Teacher info is success update'), 'info')
        return self.template()


class TeacherArea(BrowserView):
    template = ViewPageTemplateFile("template/teacher_area.pt")
    def __call__(self):
        request = self.request
        teacher_uid = self.request.cookies.get("teacher_login", "")
        teacher = api.content.get(UID=teacher_uid)
        if not teacher:
            return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
        self.teacher = teacher

        return self.template()

    def getPathname(self):
        cookie_path = api.portal.get().absolute_url_path()
        return cookie_path

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

    def getCourse(self):
        teacher_uid = self.teacher.UID()
        portal = api.portal.get()
        if portal['language_study'].has_key('latest'):
            context = portal['language_study']['latest']['class_intro']
            course = api.content.find(context=context, portal_type='Course', course_teacher=teacher_uid, sort_on='getObjPositionInParent')
            return course
        return []

    def getTwoWeekCourse(self):
        current_time = datetime.datetime.now().date()
        date_list = [current_time + datetime.timedelta(days=x) for x in range(0, 14)]
        courses = self.getCourse()
        prepareList = []
        self.courseList = []
        self.notPrepare = []
        self.todayPrepare = []
        for course in courses:
            prepares = api.content.find(context=course.getObject(), portal_type='Prepare', start_date=date_list, sort_on='getObjPositionInParent')
            if len(prepares) != 0:
                self.courseList.append(course)
                for prepare in prepares: 
                    if not prepare.getObject().file:
                        self.notPrepare.append(prepare)
                    if prepare.start_date == current_time:
                        self.todayPrepare.append(prepare) 
                prepareList.extend(prepares)

        if len(prepareList) != 0:
            prepareList.sort(key=lambda r: r.start_date)

        return prepareList


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
            field_value = getattr(item, field, '')
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
        prepare = api.content.find(context=obj, portal_type="Prepare", sort_on='getObjPositionInParent')
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


class PrepareView(BrowserView):
    template = ViewPageTemplateFile("template/prepare_view.pt")
    def __call__(self):
        request = self.request
        context = self.context

        return self.template()


class PdfEmbeded(BrowserView):
    template = ViewPageTemplateFile("template/pdf_embeded.pt")
#    template = ViewPageTemplateFile("template/search_from_id.pt")
    def __call__(self):
        request = self.request
        context = self.context

        #TODO: 老師登入權限
        if not api.user.is_anonymous():
            self.canRollcall = True
        else:
            self.canRollcall = False
        return self.template()


class Rollcall(BrowserView):
    def __call__(self):
        request = self.request
        context = self.context

        #TODO: 老師登入權限
        if api.user.is_anonymous():
            return request.response.redirect(api.portal.get().absolute_url())

        context.onCall = request.form.get('on_call').replace('||', '\n')
        context.notOnCall = request.form.get('not_on_call').replace('||', '\n')
#        import pdb; pdb.set_trace()

        return


class SearchFromId(BrowserView):

    template = ViewPageTemplateFile("template/search_from_id.pt")
    def __call__(self):
        request = self.request
        context = self.context
        portal = api.portal.get()

        id = request.form.get('id')
        self.brain = None
        if id:
            self.brain = api.content.find(context=portal['language_study']['latest'], Type='Course', id=id)
        return self.template()


class SchoolInit(BrowserView):
    template = ViewPageTemplateFile("template/school_init.pt")
    template_login = ViewPageTemplateFile("template/school_login.pt")
    def __call__(self):
        request = self.request
        hashSHA256 = request.form.get('id', '')
        school = api.content.find(hashSHA256=hashSHA256)

        if len(school) == 1:
            self.school = school[0]
        
        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            portal_catalog = getToolByName(self.context, 'portal_catalog')
            index_id = portal_catalog.Indexes['school_id']
 
            school_id = request.form.get('school_id', '')
            school_pw = request.form.get('school_pw', '')
            if request.form.get('widget-registered-btn', '') == 'widget-registered-btn':
                if school_id == self.school.school_id or school_id not in index_id.uniqueValues():
                    self.initSchool(school_id, school_pw, hashSHA256)
                else: 
                    self.context.plone_utils.addPortalMessage(_(u'This School ID is already be used'), 'error')
            else:
                self.checkLogin(school_id, school_pw)

        if len(school) != 1:
            return self.template_login()
        return self.template()

    def initSchool(self, school_id, school_pw, hashSHA256):
        alsoProvides(self.request, IDisableCSRFProtection) 
        self.school.getObject().school_id = school_id
        self.school.getObject().school_pw = school_pw
        self.school.getObject().reindexObject()

        #current_time = datetime.datetime.now().date()
        #effective_date = current_time - datetime.timedelta(days=3)
        #self.school.getObject().link_date = effective_date

        cookie_path = api.portal.get().absolute_url_path()
        self.request.response.setCookie("school_login", self.school.UID, path=cookie_path)

        return self.request.response.redirect('{}/school-area/school-area'.format(self.context.portal_url())) 

    def checkLogin(self, school_id, school_pw):
        school = api.content.find(portal_type='School', school_id=school_id, sort_on='getObjPositionInParent')
        if len(school) == 1:
            if school[0].getObject().school_pw == school_pw:

                cookie_path = api.portal.get().absolute_url_path()
                self.request.response.setCookie("school_login", school[0].UID, path=cookie_path)

                return self.request.response.redirect('{}/school-area/school-area'.format(self.context.portal_url()))

        self.context.plone_utils.addPortalMessage(_(u'Your Username or Password is not vaild'), 'error')


class SchoolArea(BrowserView):
    template = ViewPageTemplateFile("template/school_area.pt")
    def __call__(self):
        request = self.request
        school_uid = self.request.cookies.get("school_login", "")
        school = api.content.get(UID=school_uid)
        if not school:
            return self.request.response.redirect('{}/school-area/school-login'.format(self.context.portal_url()))
        self.school = school

        if request.get("widget-form-btn", "") == "widget-namelist-form":
            self.updateNamelist()
            return request.response.redirect(self.request.URL)

        return self.template()

    def getPathname(self):
        cookie_path = api.portal.get().absolute_url_path()
        return cookie_path

    def getCourse(self):
        school_uid = self.school.UID()
        course = api.content.find(portal_type='Course', course_schools=school_uid)
        return course

    def getNamelist(self, course):
        school_title = safe_unicode(self.school.title)
        school_city = safe_unicode(self.school.getParentNode().title)
        studentList = course.studentList
        nameList = ''
        otherList = ''
        if studentList:
            studentList = course.studentList.split('\r\n')
            nameList = []
            otherList = []
            for student in studentList:
                school = student.split(',')
                city  = safe_unicode(school[0])
                title = safe_unicode(school[1])
                name  = safe_unicode(school[2])
                if city == school_city and title == school_title:
                    nameList.append(name)
                else:
                    otherList.append(student)
            nameList     = '\r\n'.join(nameList)
            otherList    = '\r\n'.join(otherList)
        
        return {'nameList': nameList, 'otherList': otherList}
        
    def updateNamelist(self):
        school_title = self.school.title
        school_city = self.school.getParentNode().title
        nameHeader = '{},{},'.format(school_city.encode('utf8'), school_title.encode('utf8'))
        nameList = self.request.get('nameList', '') 
        otherList = self.request.get('otherList', '')
        uid = self.request.get('uid', '')
        course = api.content.get(UID=uid)
        studentList = otherList.split('\r\n')
        if course and nameList:
            alsoProvides(self.request, IDisableCSRFProtection)
            for name in nameList.split('\r\n'):
                if name: 
                    studentList.append(nameHeader+name)
            course.studentList = '\r\n'.join(studentList)
            self.context.plone_utils.addPortalMessage(course.title + _(u' student list already update'), 'info')
