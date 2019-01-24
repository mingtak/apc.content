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
import json
import csv
from StringIO import StringIO

logger = logging.getLogger("apc.content")


class TestPage(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request
        import pdb; pdb.set_trace()


class ZipGetSchools(BrowserView):

    def __call__(self):
        request = self.request

        zip = request.form.get('zip')

        brain = api.content.find(zip=zip)
        result = []
        for item in brain:
            result.append([item.id, item.Title])

        return json.dumps(result)


class SchoolSurvy(BrowserView):
    """ School Survy View """
    template = ViewPageTemplateFile("template/school_survy.pt")

    def getCityList(self):
        """ 取得縣市列表 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.citySorted')


    def getDistList(self):
        """ 取得鄉鎮市區列表及區碼 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.distList')


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        resultObj = portal['school_survy']
        result = {}

        if request.has_key('download'):
            return self.download()

#        if not request.has_key('_authenticator') or not request.has_key('contact'):
        if not request.has_key('contact'):
            return self.template()

        result['city'] = request.get('city')
        result['zip'] = request.get('zip')
        result['school_id'] = request.get('school_name')
        result['school_name'] = api.content.find(portal_type='School', id=result['school_id'])[0].Title
        result['contact'] = request.get('contact')
        result['phone'] = request.get('phone')
        result['cell'] = request.get('cell')
        result['email'] = request.get('email')
        result['lang-class-time'] = request.get('lang-class-time')
        if result['lang-class-time'] == '6':
            result['lang-class-time'] = '12345'
        result['lang-class-time-other'] = request.get('lang-class-time-other')

        lang = []
        for index in range(20):
            lang.append(request.get('lang-%s' % index))

        result['lang'] = lang

        try:
            jsonData = json.loads(resultObj.description)
        except:
            jsonData = []

        jsonData.append(result)
        resultObj.description = json.dumps(jsonData)
        api.portal.show_message(message=_('Survy Finish, Thanks!'), request=request)
        return self.template()


    def download(self):

        time = {'1': '周一早自習',
            '2': '周二早自習',
            '3': '周三早自習',
            '4': '周四早自習',
            '5': '周五早自習',
            '6': '早自習均可',
            '7': '其它',}

        if api.user.get_current().id != 'admin':
            return
        context = self.context
        request = self.request
        portal = api.portal.get()
        resultObj = portal['school_survy']

        result = json.loads(resultObj.description)

        output = StringIO()
        spamwriter = csv.writer(output)
#        import pdb; pdb.set_trace()
        spamwriter.writerow(['city', 'zip', 'school_id', 'school_name', 'contact', 'phone', 'cell', 'email',
                             'lang-class-time', 'lang-class-time-other',
            'lang1', 'level1',
            'lang2', 'level2',
            'lang3', 'level3',
            'lang4', 'level4',
            'lang5', 'level5',
            'lang6', 'level6',
            'lang7', 'level7',
            'lang8', 'level8',
            'lang9', 'level9',
            'lang10', 'level10',
            'lang11', 'level11',
            'lang12', 'level12',
            'lang13', 'level13',
            'lang14', 'level14',
            'lang15', 'level15',
            'lang16', 'level16',
            'lang17', 'level17',
            'lang18', 'level18',
            'lang19', 'level19',
            'lang20', 'level20',
        ])

        for item in result:
            row = [item.get('city', ' ').encode('utf-8'), item.get('zip', ' ').encode('utf-8'), item.get('school_id', ' ').encode('utf-8'),
                   item.get('school_name', ' ').encode('utf-8'), item.get('contact', ' ').encode('utf-8'),
                   item.get('phone', ' ').encode('utf-8'), item.get('cell', ' ').encode('utf-8'), item.get('email', ' ').encode('utf-8'),
                   item.get('lang-class-time', ' ').encode('utf-8'), item.get('lang-class-time-other', ' ').encode('utf-8')]
            for index in range(20):
                if item['lang'][index][1:4] != ["0", "0", "0"]:
                    row.append(item['lang'][index][0]) # 語別
                    row.append('/'.join(item['lang'][index][1:4])) # 所需級別

            spamwriter.writerow(row)
        request.response.setHeader('Content-Type', 'application/csv')
        request.response.setHeader('Content-Disposition', 'attachment; filename="school_survy.csv"')

        return output.getvalue()


class TeacherSurvy(BrowserView):
    """ Teaher Survy View """
    template = ViewPageTemplateFile("template/teacher_survy.pt")

    def getCityList(self):
        """ 取得縣市列表 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.citySorted')


    def getDistList(self):
        """ 取得鄉鎮市區列表及區碼 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.distList')


    def download(self):

        if api.user.get_current().id != 'admin':
            return
        context = self.context
        request = self.request
        portal = api.portal.get()
        resultObj = portal['teacher_survy']

        result = json.loads(resultObj.description)

        output = StringIO()
        spamwriter = csv.writer(output)
#        import pdb; pdb.set_trace()
        spamwriter.writerow(['name_han', 'han_zu', 'phone', 'cell', 'city', 'zip', 'address',
                             'lang-class-time', 'lang-class-time-other',
            'lang1', 'level1',
            'lang2', 'level2',
            'lang3', 'level3',
            'lang4', 'level4',
            'lang5', 'level5',
            'lang6', 'level6',
            'lang7', 'level7',
            'lang8', 'level8',
            'lang9', 'level9',
            'lang10', 'level10',
            'lang11', 'level11',
            'lang12', 'level12',
            'lang13', 'level13',
            'lang14', 'level14',
            'lang15', 'level15',
            'lang16', 'level16',
            'lang17', 'level17',
            'lang18', 'level18',
            'lang19', 'level19',
            'lang20', 'level20',
        ])

        for item in result:
            row = [item.get('name_han').encode('utf-8'), item.get('name_zu').encode('utf-8'),
                   item.get('phone'), item.get('cell'),
                   item.get('city').encode('utf-8'), item.get('zip'), item.get('address').encode('utf-8'),
                   item.get('lang-class-time', ' ').encode('utf-8'), item.get('lang-class-time-other', ' ').encode('utf-8')]
            for index in range(20):
                if type(item['lang'][index]) == type([]):
                    row.append(item['lang'][index][0])

                    primary = '1' if 'primary' in item['lang'][index] else '0'
                    intermediate = '1' if 'intermediate' in item['lang'][index] else '0'
                    advanced = '1' if 'advanced' in item['lang'][index] else '0'

                    row.append('/'.join([primary, intermediate, advanced]))

#            import pdb; pdb.set_trace()
            spamwriter.writerow(row)
        request.response.setHeader('Content-Type', 'application/csv')
        request.response.setHeader('Content-Disposition', 'attachment; filename="techer_survy.csv"')

        return output.getvalue()


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        resultObj = portal['teacher_survy']
        result = {}

        if request.has_key('download'):
            return self.download()

#        import pdb;pdb.set_trace()
#        if not request.has_key('_authenticator') or not request.has_key('name_han'):
        if not request.has_key('name_han'):
            return self.template()

        result['name_han'] = request.get('name_han')
        result['name_zu'] = request.get('name_zu')
        result['phone'] = request.get('phone')
        result['cell'] = request.get('cell')
        result['city'] = request.get('city')
        result['zip'] = request.get('zip')
        result['address'] = request.get('address')
        result['lang-class-time'] = request.get('lang-class-time')
        if result['lang-class-time'] == '6':
            result['lang-class-time'] = '12345'
        result['lang-class-time-other'] = request.get('lang-class-time-other')

        lang = []
        for index in range(20):
            lang.append(request.get('lang-%s' % index))

        result['lang'] = lang

        try:
            jsonData = json.loads(resultObj.description)
        except:
            jsonData = []

        jsonData.append(result)
        resultObj.description = json.dumps(jsonData)
        api.portal.show_message(message=_('Survy Finish, Thanks!'), request=request)
#        import pdb;pdb.set_trace()
        return self.template()


class MakeUpListing(BrowserView):
    """ Make Up Listing View """
    template = ViewPageTemplateFile("template/make_up_listing.pt")

    def makeUp(self, uid, makeUpDay, alreadyMakeUp, leave):
        if not (makeUpDay and leave):
            api.portal.show_message(message=u'補課日期未填或公告內容未填', request=self.request, type='error')
            return
        obj = api.content.find(UID=uid)[0].getObject()
        obj.makeUp = alreadyMakeUp
        obj.title = safe_unicode(makeUpDay)
        obj.makeUpDay = safe_unicode(makeUpDay)
        obj.leave = safe_unicode(leave)
        api.portal.show_message(message=u'已更新 %s 補課資訊' % obj.title, request=self.request, type='info')


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        self.brain = api.content.find(portal_type='Prepare', leaveALesson=True)

        uid = request.form.get('uid')
        makeUpDay = request.form.get('make-up-day')
        alreadyMakeUp = True if request.form.get('already-make-up') else False
        leave = request.form.get('leave')
        if uid:
            self.makeUp(uid, makeUpDay, alreadyMakeUp, leave)
            return self.template()

        return self.template()


class SchoolIdPwdList(BrowserView):

    template = ViewPageTemplateFile("template/school_id_pwd_list.pt")
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        brain = api.content.find(portal_type='Course')
        schoolList = []
        self.result = []
        for item in brain:
            obj = item.getObject()
            if obj.school:
                for school in obj.school:
                    if school.to_object.id in schoolList:
                        continue
                    else:
                        schObj = school.to_object
                        schoolList.append(schObj.id)
                        self.result.append('%s\t%s\t%s\t%s\n' % (schObj.id, schObj.title, schObj.school_id, schObj.school_pw))
                        logger.info('append ok, %s' % schObj.title)
        return self.template()


class TeacherIdPwdList(BrowserView):

    template = ViewPageTemplateFile("template/teacher_id_pwd_list.pt")
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        brain = api.content.find(portal_type='Teacher')
        teacherList = []
        self.result = []
        for item in brain:
            obj = item.getObject()
            if obj.teacher_id:
                schObj = obj
                teacherList.append(obj.id)
                self.result.append('%s\t%s\t%s\t%s\n' % (schObj.title, schObj.teacher_id, schObj.teacher_pw, schObj.id))
                logger.info('append ok, %s' % schObj.title)
        return self.template()


class AllSchoolList(BrowserView):

    template = ViewPageTemplateFile("template/all_school_list.pt")
    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        self.brain = api.content.find(portal_type='School', sort_on='id')
        return self.template()


class AllCourseList(BrowserView):

    template = ViewPageTemplateFile("template/all_course_list.pt")

    def getWeekDay(self, id):
        year = int(id.split('_')[-3])
        month = int(id.split('_')[-2])
        day = int(id.split('_')[-1])
        return _(datetime.datetime(year, month, day).strftime('%A'))


    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        self.brain = api.content.find(portal_type='Course', sort_on='id')
        return self.template()


""" 
class SetSchoolPwd(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        brain = api.content.find(portal_type='School')
        for item in brain:
            obj = item.getObject()
            id = 's%s' % item.id
            pwd = 's%s' % item.id[::-1]
            obj.school_id = id
            obj.school_pw = pwd
            obj.reindexObject()
            logger.info('update ok, %s' % item.Title)
        return
"""

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

#        import pdb; pdb.set_trace()
        if int(can_lv) and int(req_lv): # 開課程度吻合
            import pdb; pdb.set_trace()
            if set(school['lang-class-time']) & set(school['lang-class-time']): # 開課時間吻合
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

        # 讀取學校及教師調查表csv檔
        teacher_survy = request.get('teacher_survy', '')
        school_survy = request.get('school_survy', '')

        tFile = StringIO(teacher_survy.read())
        tReader = csv.DictReader(tFile, delimiter=',')
        teachers = []
        for item in tReader:
            teachers.append(item)

        sFile = StringIO(school_survy.read())
        sReader = csv.DictReader(sFile, delimiter=',')
        schools = []
        for item in sReader:
            schools.append(item)
#        import pdb; pdb.set_trace()

        # min costudy schools(min_sc)
        self.min_sc=int(request.form.get('min_sc', 3))
        # max costudy schools(max_sc) and students(max_st) limit
        self.max_sc=int(request.form.get('max_sc', 6))
        self.max_st=int(request.form.get('max_st', 10))

#        factory1 = getUtility(IVocabularyFactory, 'apc.content.ClassTime')
#        self.vocaClassTime = factory1(context)

#        teachers = portal['teacher'].getChildNodes()
#        schools = api.content.find(context=portal['school'], portal_type='School')

        # 確認可開班狀況, 大課表
        self.courseTable = {}
        for teacher in teachers:
#            import pdb; pdb.set_trace()
            for item in teacher['lang-class-time']:
                # [學生數, 開課級別]
                self.courseTable['%s_%s' % (teacher['name_han'], item)] = [0, '', '']

        for teacher in teachers:
            # 老師能教
            canTeach = {}

            for i in range(1, 21):
                if teacher['lang%s' % i]:
                    canTeach[teacher['lang%s' % i]] = teacher['level%s' % i]

#            import pdb; pdb.set_trace()

            for school in schools:

                # 學校需要
                reqLang = []
                for i in range(1, 21):
                    # 逐個語言比對
#                    language = item.split(',')[1]

#                    import pdb; pdb.set_trace()
                    if not school['lang%s' % i]:
#language in canTeach.keys():
                        continue

                    if school['lang%s' % i] in canTeach:
                        language = school['lang%s' % i]
                        req_lv_1, req_lv_2, req_lv_3 = school['level%s' % i].split('/')
                        can_lv_1, can_lv_2, can_lv_3 = canTeach[language].split('/')
                    else:
                        continue

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

            if request.form.has_key('file-upload-widget'):
                prepareList = request.get('prepare', '')
                for prepare in prepareList:
                    uid = prepare.get('uid', '')
                    item = api.content.get(UID=uid)
                    url = item.absolute_url()
                    upload_topic = prepare.get('topic', '')
                    upload_text  = prepare.get('description', '')
                    data = {"description": upload_text, "topic": upload_topic}

                    data.update({"vacation": False})
                    if prepare.get('vacation', '') == 'true':
                        data.update({"vacation": True})

                    file = prepare.get('file', '')
                    file_data = self.checkUploadFile(file, 'file') 
                    if file_data: 
                        data.update(file_data)

                    file2 = prepare.get('file2', '')
                    file_data2 = self.checkUploadFile(file2, 'file2') 
                    if file_data2: 
                        data.update(file_data2)

                    file3 = prepare.get('file3', '')
                    file_data3 = self.checkUploadFile(file3, 'file3') 
                    if file_data3: 
                        data.update(file_data3)

                    for del_file in [prepare.get('del_file', ''), prepare.get('del_file2', ''), prepare.get('del_file3', '')]:
                        if del_file: 
                            data.update({del_file: ''}) 
                    headers = {
                        'Accept': "application/json",
                        'Content-Type': "application/json",
                        'Authorization': "Basic YWRtaW46MTIzNDU2",
                    }
                    response = requests.request("PATCH", url, headers=headers, json=data)
                self.request.response.redirect(self.request.URL)
            return self.template()
        else:
            return self.request.response.redirect('{}/teacher-area/teacher-area'.format(self.context.portal_url()))

    def checkUploadFile(self, file, name):
        file_data = file.read() 
        if file_data: 
            return { 
                     name: { 
                     "content-type": file.headers['content-type'], 
                     "filename": file.filename, 
                     "encoding": "base64", 
                     "data": file_data.encode('base64') 
                     } 
                   }
        return 

    def getCourse(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
        return course

    def getPrepare(self):
        courseUID = self.course.UID
        course = api.content.get(UID=courseUID)
#        prepare = api.content.find(context=course, portal_type="Prepare",
#                                   start={'query':DateTime(), 'range':'min'}, sort_on='getObjPositionInParent')
        prepare = api.content.find(context=course, portal_type="Prepare", sort_on='getObjPositionInParent')
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
        upload_topic = request.form.get('topic', '')
        upload_text = request.form.get('description', '')

        data = {"description": upload_text, "upload_topic": upload_topic}
        data.update({"vacation": False})
        if request.get('vacation', '') == 'true':
            data.update({"vacation": True})

        file = request.get('file', '')
        file_data = self.checkUploadFile(file, 'file') 
        if file_data: 
            data.update(file_data)

        file2 = request.get('file2', '')
        file_data2 = self.checkUploadFile(file2, 'file2') 
        if file_data2: 
            data.update(file_data2)

        file3 = request.get('file3', '')
        file_data3 = self.checkUploadFile(file3, 'file3') 
        if file_data3: 
            data.update(file_data3)

        for del_file in [request.get('del_file', ''), request.get('del_file2', ''), request.get('del_file3', '')]:
            if del_file: 
                data.update({del_file: ''})
 
        url = self.prepare.getURL()
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'Authorization': "Basic YWRtaW46MTIzNDU2",
        }
        response = requests.request("PATCH", url, headers=headers, json=data)

    def checkUploadFile(self, file, name):
        file_data = file.read() 
        if file_data: 
            return { 
                     name: { 
                     "content-type": file.headers['content-type'], 
                     "filename": file.filename, 
                     "encoding": "base64", 
                     "data": file_data.encode('base64') 
                     } 
                   }
        return 


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
            teacherFields = ['certification', 'study', 'qualified_teacher', 'ethnic_teacher', 'education', 'experience', 'teaching_years', 'remarks', 'email', 'gender', 'nameSpell', 'aboriginalsLang']
            data = {}
            url = self.teacher.getURL()
            headers = {
                'Accept': "application/json",
                'Content-Type': "application/json",
                'Authorization': "Basic YWRtaW46MTIzNDU2",
            }
            for field in teacherFields:
                value = request.form.get(field, '')
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
            return self.request.response.redirect('{}/teacher-area/teacher-info'.format(self.context.portal_url()))
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
        fields = ['nameSpell'     , 'aboriginalsLang', 'localLang' , 'certification'    , 'study' , 'qualified_teacher', \
                  'ethnic_teacher', 'education'      , 'experience', 'teaching_years'   , 'remarks'] 
        fieldsName = {'nameSpell' : _(u'Name Spell')           , 'aboriginalsLang'  : _(u'Aboriginals Language'),
                      'localLang' : _(u'Local Language')       , 'certification'    : _(u'Ethnic language certification'),
                      'study'     : _(u'Revitalization study') , 'qualified_teacher': _(u'Teaching class (Qualified teacher)'), 
                      'ethnic_teacher': _(u'Teaching class (Ethnic teacher)'), 'education'      : _(u'Education'),
                      'experience'    : _(u'work experience')                , 'teaching_years' : _(u'Teaching years'),
                      'remarks'       : _(u'Remarks')} 
        fieldsDict = OrderedDict()
        for field in fields:
            field_value = getattr(item, field, '')
            if field_value:
                fieldsDict.update({fieldsName[field]: field_value})
        if fieldsDict.has_key(fieldsName['localLang']):
            fieldsDict.pop(fieldsName['localLang'])
#            localLangValue = '\r\n'.join([lang.split(',')[1] for lang in fieldsDict[fieldsName['localLang']].split('/')])
#            fieldsDict[fieldsName['localLang']] = localLangValue
#            fieldsDict[fieldsName['localLang']] = item.aboriginalsLang
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


class TeacherChangePW(BrowserView):
    template = ViewPageTemplateFile("template/teacher_changePW.pt")
    def __call__(self):
        request = self.request
        teacher_uid = self.request.cookies.get("teacher_login", "")
        teacher = api.content.get(UID=teacher_uid)
        if not teacher:
            return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
        self.teacher = teacher
        
        if request.get('widget-resetPW-btn', '') == 'widget-resetPW-btn':
            current_pw = request.get('current_pw', '') 
            change_pw = request.get('teacher_pw', '')
            if self.checkPW(current_pw):
                self.changePW(change_pw)
            else: 
                self.context.plone_utils.addPortalMessage(_(u'Your current password is not vaild'), 'error')

        return self.template()

    def getPathname(self):
        cookie_path = api.portal.get().absolute_url_path()
        return cookie_path

    def checkPW(self, currentPW):
        if currentPW == self.teacher.teacher_pw:
            return True
        return False

    def changePW(self, change_pw):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.teacher.teacher_pw = change_pw

        cookie_path = api.portal.get().absolute_url_path()
        self.request.response.setCookie("teacher_login", '', path=cookie_path)
	self.context.plone_utils.addPortalMessage(_(u'Your password is already change please login again'), 'info')
        return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))


class PloneRootView(BrowserView):
    pass


class CourseView(BrowserView):
    pass


class CourseStudent(BrowserView):
    def getStudents(self):
        courses = api.content.find(portal_type="Course")
        return courses


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
            try:
                localLangValue = '\r\n'.join([lang.split(',')[1] for lang in fieldsDict[fieldsName['localLang']].split('/')])
            except:
                localLangValue = ''
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
            try:
                localLangValue = '\r\n'.join([lang.split(',')[1] for lang in fieldsDict[fieldsName['localLang']].split('/')])
            except:
                localLangValue = ''
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

        teacher_uid = self.request.cookies.get("teacher_login", "")
        teacher = api.content.get(UID=teacher_uid)
        if teacher or not api.user.is_anonymous():
            self.canRollcall = True
        else:
            self.canRollcall = False
        return self.template()


class CastView(BrowserView):
    template = ViewPageTemplateFile("template/cast_view.pt")

    def __call__(self):

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
            self.brain = api.content.find(context=portal['language_study']['latest'], portal_type='Course', id=id)
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

        if request.get("widget-form-btn", "") == "widget-email-form":
            self.updateEmail()
            return request.response.redirect(self.request.URL)

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
            studentList = course.studentList.strip().split('\r\n')
            nameList = []
            otherList = []
            for student in studentList:
                school = student.split(',')
#                import pdb;pdb.set_trace()
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
        
    def updateEmail(self):
        name      = self.request.get('name', '') 
        telephone = self.request.get('telephone', '') 
        phone     = self.request.get('phone', '') 
        email     = self.request.get('email', '') 
        if email:
            alsoProvides(self.request, IDisableCSRFProtection)
            self.school.name      = name     
            self.school.telephone = telephone
            self.school.phone     = phone    
            self.school.email     = email    
            self.context.plone_utils.addPortalMessage(_(u'Email already update'), 'info')

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


class SchoolChangePW(BrowserView):
    template = ViewPageTemplateFile("template/school_changePW.pt")
    def __call__(self):
        request = self.request
        school_uid = self.request.cookies.get("school_login", "")
        school = api.content.get(UID=school_uid)
        if not school:
            return self.request.response.redirect('{}/school-area/school-login'.format(self.context.portal_url()))
        self.school = school
        
        if request.get('widget-resetPW-btn', '') == 'widget-resetPW-btn':
            current_pw = request.get('current_pw', '') 
            change_pw = request.get('school_pw', '')
            if self.checkPW(current_pw):
                self.changePW(change_pw)
            else: 
                self.context.plone_utils.addPortalMessage(_(u'Your current password is not vaild'), 'error')

        return self.template()

    def getPathname(self):
        cookie_path = api.portal.get().absolute_url_path()
        return cookie_path

    def checkPW(self, currentPW):
        if currentPW == self.school.school_pw:
            return True
        return False

    def changePW(self, change_pw):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.school.school_pw = change_pw

        cookie_path = api.portal.get().absolute_url_path()
        self.request.response.setCookie("school_login", '', path=cookie_path)
	self.context.plone_utils.addPortalMessage(_(u'Your password is already change please login again'), 'info')
        return self.request.response.redirect('{}/school-area/school-login'.format(self.context.portal_url()))


class LiveListing(BrowserView):
    """ Live Listing View """
    template = ViewPageTemplateFile("template/live_listing.pt")

    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()
        self.brain = api.content.find(portal_type='LiveClass')
        return self.template()


class CourseSchedule(BrowserView):

    template = ViewPageTemplateFile("template/course_schedule.pt")

    def getWeekDay(self, id):
        year = int(id.split('_')[-3])
        month = int(id.split('_')[-2])
        day = int(id.split('_')[-1])
        return datetime.datetime(year, month, day).strftime('%w')


    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        self.brain = api.content.find(portal_type='Course', sort_on='id')
        return self.template()


class AdminCourseSchedule(BrowserView):

    template = ViewPageTemplateFile("template/admin_course_schedule.pt")

    def getWeekDay(self, id):
        year = int(id.split('_')[-3])
        month = int(id.split('_')[-2])
        day = int(id.split('_')[-1])
        return datetime.datetime(year, month, day).strftime('%w')


    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

        self.brain = api.content.find(portal_type='Course', sort_on='id')
        return self.template()

