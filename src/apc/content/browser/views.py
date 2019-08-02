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
from mingtak.ECBase.browser.views import SqlObj
import codecs
import os
import xlwt
import random
#import adal
#from pypowerbi.dataset import Column, Table, Dataset
#from pypowerbi.client import PowerBIClient

import sys
reload(sys)
sys.setdefaultencoding('utf8')


logger = logging.getLogger("apc.content")


class UpdatePageCount(BrowserView):

    def __call__(self):
        return
        sqlObj = SqlObj()
        brain = api.content.find(Type="Prepare")

        for item in brain:
            obj = item.getObject()
            if not (obj.file or obj.file2 or obj.file3 or obj.embeded):
                parent = obj.getParentNode()
                title = '%s-%s' % (parent.title, obj.title)
                init = random.randint(1, 10)
                sqlStr = """INSERT INTO page_count(url, title, count)
                            VALUES('{}', '{}', {}) ON DUPLICATE KEY
                            UPDATE count = count + {}, title = '{}'""".format(item.getURL(), title, init, init, title)
                sqlObj.execSql(sqlStr)
                continue

            parent = obj.getParentNode()
            title = '%s-%s' % (parent.title, obj.title)
            init = random.randint(100, 200)
            sqlStr = """INSERT INTO page_count(url, title, count)
                        VALUES('{}', '{}', {}) ON DUPLICATE KEY
                        UPDATE count = count + {}, title = '{}'""".format(item.getURL(), title, init, init, title)
            sqlObj.execSql(sqlStr)
            logger.info('PAGE COUNT: %s: %s' % (item.getURL(), init))

        return 'OK'



class GernalLogin(BrowserView):
    template = ViewPageTemplateFile("template/gernal_login.pt")
    def __call__(self):
        return self.template()


class VerifyStudent(BrowserView):
    template = ViewPageTemplateFile("template/verify_student.pt")
    def __call__(self):
        request = self.request
        execSql = SqlObj()
        mode = request.get('mode')
        id = request.get('id')
        if id and mode:
            sqlStr = """UPDATE student SET %s = 1 WHERE id = %s""" %(mode, id)
            execSql.execSql(sqlStr)
            api.portal.show_message(message='已通過'.decode('utf-8') if mode == 'verify' else '已刪除'.decode('utf-8'), request=request)


        sqlStr = """SELECT * FROM student WHERE verify = 0 AND cancel = 0 ORDER BY language"""
        self.studentList = execSql.execSql(sqlStr)

        return self.template()


class SatisfactionSurvy(BrowserView):
    template = ViewPageTemplateFile("template/satisfaction_survy.pt")

    def getCityList(self):
        """ 取得縣市列表 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.citySorted')


    def getDistList(self):
        """ 取得鄉鎮市區列表及區碼 """
        return api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.distList')

    def __call__(self):
        request = self.request
        city = request.get('city')
        if city:
            zip = request.get('zip')
            school_id = request.get('school_name')
            school_name = api.content.find(portal_type='School', id=school_id)[0].Title
            contact = request.get('contact')
            phone = request.get('phone')
            cell = request.get('cell')
            email = request.get('email')
            identity = request.get('identity')
            anw1 = request.get('anw1')
            anw2 = request.get('anw2')
            anw3 = request.get('anw3')
            anw4 = request.get('anw4')
            anw5 = request.get('anw5')

            execSql = SqlObj()
            sqlStr = """INSERT INTO `satisfaction`(`identity`, `contact`, `city`, `zip`, `school_name`, `phone`, `cell`, `email`, `anw1`,
                     `anw2`, `anw3`, `anw4`, `anw5`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                     """.format(identity, contact, city, zip, school_name, phone, cell, email, anw1, anw2, anw3, anw4, anw5)
            execSql.execSql(sqlStr)

            api.portal.show_message(message='填寫成功！'.decode('utf-8'), request=request)

        return self.template()


class InsertStudent(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        latest = api.content.find(context=portal["language_study"]["latest"]["class_intro"], depth=1, portal_type='Course')
        first = api.content.find(context=portal["language_study"]["107_1"]["class_intro"], depth=1, portal_type='Course')
        execSql = SqlObj()
        self.insertData(latest)
        self.insertData(first)

    def insertData(self, data):
        execSql = SqlObj()
        for i in data:
            obj = i.getObject()
            studentList = obj.studentList
            title = obj.title
            course = title[:6].encode('utf-8')
            language = title[6:].encode('utf-8')
            if studentList:
                for student in studentList.split('\r\n'):
                    if student:
                        try:
                            temp = student.split(',')
                            try:
                                county = temp[0].encode('utf-8')
                            except:
                                county = temp[0]
                            try:
                                school = temp[1].encode('utf-8')
                            except:
                                school = temp[1]
                            try:
                                name = temp[2].split('(')[0].encode('utf-8')
                            except:
                                name = temp[2]
                            sqlStr = """INSERT INTO student(county, school, course, language, name) VALUES('{}', '{}', '{}', '{}', '{}')
                                     """.format(county, school, course, language, name)
                            execSql.execSql(sqlStr)
                        except Exception as e:
                            print e
                            import pdb;pdb.set_trace()


class ShowChart(BrowserView):
    template = ViewPageTemplateFile("template/show_chart.pt")
    template2 = ViewPageTemplateFile("template/lang_chart.pt")
    template3 = ViewPageTemplateFile("template/student_rate_chart.pt")
    template4 = ViewPageTemplateFile("template/not_on_call_detail.pt")
    template5 = ViewPageTemplateFile("template/page_count.pt")
    template6 = ViewPageTemplateFile("template/student_count.pt")
    template7 = ViewPageTemplateFile("template/satisfaction_result.pt")

    def __call__(self):
        request = self.request
        mode = request.get('mode')
        period = request.get('period')
        search = request.get('search')
        selected_course = request.get('selected_course')
        portal = api.portal.get()
        execSql = SqlObj()
        lang_cata = {
            '阿美語': '南勢阿美語 秀姑巒阿美語 海岸阿美語 馬蘭阿美語 恆春阿美語', 
            '泰雅語': '賽考利克泰雅語 澤敖利泰雅語 汶水泰雅語 萬大泰雅語 四季泰雅語 澤敖利泰雅語', 
            '賽夏語': '賽夏語', 
            '邵語': '邵語',    
            '賽德克語': '都達語 德固達雅語 德魯固語', 
            '布農語': '卓群布農語 卡群布農語 丹群布農語 巒群布農語 郡群布農語' , 
            '排灣語': '東排灣語 北排灣語 中排灣語 南排灣語', 
            '魯凱語': '東魯凱語 霧臺魯凱語 大武魯凱語 多納魯凱語 茂林魯凱語 萬山魯凱語', 
            '太魯閣語': '太魯閣語', 
            '噶瑪蘭語': '噶瑪蘭語', 
            '鄒語': '鄒語', 
            '卡那卡那富語': '卡那卡那富語', 
            '拉阿魯哇語': '拉阿魯哇語', 
            '卑南語': '南王卑南語 知本卑南語 初鹿卑南語 建和卑南語', 
            '雅美語': '雅美語', 
            '撒奇萊雅語': '撒奇萊雅語'
        }

        if search:
            course = api.content.find(context=portal['language_study'][period]['class_intro'], depth=1, portal_type='Course')
            courseList = []
            for i in course:
                courseList.append({'title': i.Title, 'id': i.id})
            return json.dumps(courseList)

        if mode == 'lang':
            course = api.content.find(context=portal['language_study'][period]['class_intro'], depth=1, portal_type='Course')
            count = {'阿美語':0, '泰雅語': 0, '賽夏語': 0, '邵語': 0, '賽德克語': 0, '布農語': 0, '排灣語': 0, '魯凱語': 0, 
            '太魯閣語': 0, '噶瑪蘭語': 0, '鄒語': 0, '卡那卡那富語': 0, '拉阿魯哇語': 0, '卑南語': 0, '雅美語': 0, '撒奇萊雅語': 0}
            total = 0
            for i in course:
                title = i.Title[6:]
                flag = True
                for k,v in lang_cata.items():
                    if title in v.split(' '):
                        count[k] += 1
                        total += 1
                        flag = False
                        continue
            self.count = json.dumps(count)
            self.total = total
            return self.template2()
        elif mode == 'student_rate':

            start = request.get('start')
            end = request.get('end')
            month = request.get('month')

            sqlStr = """SELECT * FROM attend WHERE date """

            if start and end:
                sqlStr += """BETWEEN '{}' AND '{}'""".format(start, end)
            elif month:
                sqlStr += """LIKE '{}'""".format(month + '%%')

            result = execSql.execSql(sqlStr)
            data = {}
            count = {'onCall': 0, 'notOnCall': 0}
            for item in result:
                obj = dict(item)
                course = obj['course'][6:].encode('utf-8')
                status = obj['status']
                count[status] += 1
                for k,v in lang_cata.items():
                    if course in v.split(' '):
                        if data.has_key(k):
                            data[k][status].append(obj)
                        else:
                            data[k] = {
                                'onCall': [obj] if status == 'onCall' else [],
                                'notOnCall': [obj] if status == 'notOnCall' else []
                            }
                        continue
            self.start = start
            self.end = end
            self.month = month
            self.count = json.dumps(count)
            self.data = data
            return self.template3()

        elif mode == 'notOnCallDetail':
            #已無用
            start = request.get('start')
            end = request.get('end')
            month = request.get('month')

            if start and end:
                sqlStr = """SELECT * FROM attend WHERE date BETWEEN '{}' AND '{}'""".format(start, end)

            elif month:
                sqlStr = """SELECT * FROM attend WHERE date LIKE '{}'""".format(month + '%%')

            result = execSql.execSql(sqlStr)

            count = {}
            for item in result:
                obj = dict(item)
                course = obj['course'][6:].encode('utf-8')
                status = obj['status']
                for k,v in lang_cata.items():
                    if course in v.split(' '):
                        if count.has_key(k):
                            count[k]['出席' if status == 'onCall' else '缺席'] += 1
                            if status == 'notOnCall':
                                count[k]['缺席資料'].append(obj)
                        else:
                            count[k] = {
                                '出席': 1 if status == 'onCall' else 0,
                                '缺席':1 if status == 'notOnCall' else 0,
                                '缺席資料': [obj] if status == 'notOnCall' else []
                            }
                        continue
            self.count = count


            return self.template4()
        elif mode == 'page_count':
            period = request.get('period')
            url =  'http://apc2.17study.com.tw/language_study/%s/class_intro/' %period

            sqlStr = """SELECT url,count,title FROM page_count WHERE url LIKE '{}%%'""".format(url)

            self.count = execSql.execSql(sqlStr)
            return self.template5()
        elif mode == 'number':
            number_period = request.get('number_period')

            sqlStr = """SELECT language FROM student WHERE course like '{}%%' AND verify = 1 AND cancel = 0""".format(number_period)
            result = execSql.execSql(sqlStr)

            count = {'阿美語':0, '泰雅語': 0, '賽夏語': 0, '邵語': 0, '賽德克語': 0, '布農語': 0, '排灣語': 0, '魯凱語': 0, 
            '太魯閣語': 0, '噶瑪蘭語': 0, '鄒語': 0, '卡那卡那富語': 0, '拉阿魯哇語': 0, '卑南語': 0, '雅美語': 0, '撒奇萊雅語': 0}
            for lang in result:
                for k,v in lang_cata.items():
                    if lang[0].encode('utf-8') in v.split(' '):
                        count[k] += 1
                        continue
            self.count = count
            self.total = len(result)
            return self.template6()
        elif mode == 'satisfaction':
            sqlStr = """SELECT anw1, anw2, anw3, anw4, anw5 FROM satisfaction"""
            result = execSql.execSql(sqlStr)
            count = {
                        'anw1': {'非常滿意': 0, '滿意': 0, '普通': 0, '不滿意': 0, '非常不滿意': 0},
                        'anw2': {'非常滿意': 0, '滿意': 0, '普通': 0, '不滿意': 0, '非常不滿意': 0},
                        'anw3': {'非常滿意': 0, '滿意': 0, '普通': 0, '不滿意': 0, '非常不滿意': 0},
                        'anw4': {'非常滿意': 0, '滿意': 0, '普通': 0, '不滿意': 0, '非常不滿意': 0},
                        'anw5': {'非常滿意': 0, '滿意': 0, '普通': 0, '不滿意': 0, '非常不滿意': 0},
                    }
            for item in result:
                obj = dict(item)
                anw1 = obj['anw1'].encode('utf-8')
                anw2 = obj['anw2'].encode('utf-8')
                anw3 = obj['anw3'].encode('utf-8')
                anw4 = obj['anw4'].encode('utf-8')
                anw5 = obj['anw5'].encode('utf-8')
                count ['anw1'][anw1] += 1
                count ['anw2'][anw2] += 1
                count ['anw3'][anw3] += 1
                count ['anw4'][anw4] += 1
                count ['anw5'][anw5] += 1
            self.count = json.dumps(count)
            return self.template7()
        else:
            self.brain = api.content.find(portal_type='LiveClass')
            return self.template()

        if api.is_anonymous():
            self.call_powerbi()


    def call_powerbi(self):
        # you might need to change these, but i doubt it
        authority_url = 'https://login.windows.net/common'
        resource_url = 'https://analysis.windows.net/powerbi/api'
        api_url = 'https://api.powerbi.com'

        # change these to your credentials
        client_id = '871c010f-5e61-4fb1-83ac-98610a7e9110'
        username = 'andy@mingtak.com.tw'
        password = '!QAZ@WSX' #假，資料移轉時請改輸入正確密碼，或由下一家提供

        # first you need to authenticate using adal
        context = adal.AuthenticationContext(authority=authority_url,
                                             validate_authority=True,
                                             api_version=None)

        # get your authentication token
        token = context.acquire_token_with_username_password(resource=resource_url,
                                                             client_id=client_id,
                                                             username=username,
                                                             password=password)

        # create your powerbi api client
        client = PowerBIClient(api_url, token)

        # create your columns
        columns = []
        columns.append(Column(name='id', data_type='Int64'))
        columns.append(Column(name='name', data_type='string'))
        columns.append(Column(name='is_interesting', data_type='boolean'))
        columns.append(Column(name='cost_usd', data_type='double'))
        columns.append(Column(name='purchase_date', data_type='datetime'))

        # create your tables
        tables = []
        tables.append(Table(name='AnExampleTableName', columns=columns))

        # create your dataset
        dataset = Dataset(name='AnExampleDatasetName', tables=tables)

        # post your dataset!
        client.datasets.post_dataset(dataset)
        return


class TestPage(BrowserView):

    index = ViewPageTemplateFile("template/testpage.pt")
    course_template = ViewPageTemplateFile("template/test_course.pt")

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request

        self.teacher = api.content.find(portal_type='Teacher')
        self.course = api.content.find(portal_type='Course')
        return self.course_template()
#        return self.index()

        import pdb; pdb.set_trace()


class TeacherReviewPage(BrowserView):

    template = ViewPageTemplateFile("template/teacher_review_page.pt")

    def accept(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        uid = request.get('uid')
        title = request.get('title')
        obj = api.content.find(UID=uid)[0].getObject()

        teacher = api.content.find(Title=title, context=portal['teacher'], sort_on="id")[0].getObject()
        teacher.image = obj.image
        teacher.gender = obj.gender
        teacher.nameSpell = obj.nameSpell
        teacher.aboriginalsLang = obj.aboriginalsLang
        teacher.certification = obj.certification
        teacher.study = obj.study
        teacher.qualified_teacher = obj.qualified_teacher
        teacher.ethnic_teacher = obj.ethnic_teacher
        teacher.education = obj.education
        teacher.teaching_years = obj.teaching_years
        teacher.remarks = obj.remarks
        teacher.experience = obj.experience

        teacher.reindexObject()

        api.content.delete(obj=obj)


    def reject(self):
        context = self.context
        request = self.request

        uid = request.get('uid')
        obj = api.content.find(UID=uid)[0].getObject()
        api.content.delete(obj=obj)
        return


    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request

        action = request.form.get('action')
        if action == 'accept':
            self.accept()
        elif action == 'reject':
            self.reject()

#        import pdb; pdb.set_trace()
        return self.template()


class AboutView(BrowserView):

    template = ViewPageTemplateFile("template/about_view.pt")

    def __call__(self):

        return self.template()


class LeaveListing(BrowserView):

    template = ViewPageTemplateFile("template/leave_listing.pt")

    def __call__(self):

        self.brain = api.content.find(leaveALesson=True, sort_on='modified', sort_order='reverse')

        return self.template()


class ContactView(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request

        mailTo = {
            'mailTo_1': api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.mailTo_1'),
            'mailTo_2': api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.mailTo_2'),
            'mailTo_3': api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.mailTo_3'),
            'mailTo_4': api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.mailTo_4'),
            'mailTo_5': api.portal.get_registry_record('mingtak.ECBase.browser.configlet.ICustom.mailTo_5'),
        }

        categories = {
            'mailTo_1': '族語師資教學',
            'mailTo_2': '直播共學諮詢',
            'mailTo_3': '共學小組聯絡',
            'mailTo_4': '平台系統操作',
            'mailTo_5': '系統設備叫修',
        }


        name = request.form.get('name')
        email = request.form.get('email')
        content = request.form.get('content')
        phone = request.form.get('phone')
        org = request.form.get('org')
        category = request.form.get('category')


        message = "姓名:{}\nEmail:{}\n電話:{}\n單位名稱:{}\n留言分類:{}\n留言內容:{}".format(name, email, phone, org, categories[category], content)
        api.portal.send_email(
            recipient=mailTo[category],
            sender="noreply@17study.com.tw",
            subject="經由 原住民族語直播共學平台 寄來的 聯絡我們 表單通知",
            body=message,
        )

        api.portal.show_message(message=u'系統已收到您聯絡訊息，感謝您的寶貴意見', request=request)
        request.response.redirect('%s/contact' % portal.absolute_url())


class CopyCourse(BrowserView):
    """ 將107第1學期的課，copy到107第2學期 """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request
        oldFolder = portal['language_study']['107_1']['class_intro']
        newFolder = portal['language_study']['latest']['class_intro']

        courses = oldFolder.getChildNodes()
        for course in courses:
            # copy item
            newId = course.id.replace('1071', '1072')
            newCourse = api.content.copy(source=course, target=newFolder, id=newId)
            # delete prepares
            items = newCourse.getChildNodes()
            api.content.delete(objects=list(items))
            # rename / reindex Title index
            newCourse.title = newCourse.title.replace('1071', '1072')
            newCourse.reindexObject(idxs=['Title'])
            logger.info('Create new Course OK, %s' % newCourse.title)

#        import pdb; pdb.set_trace()


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
#        result['lang-class-time'] = request.get('lang-class-time')

# 可上課時間採 JOSN, 方便後續媒合
        result['class-time'] = json.dumps(request.get('time'))
#        result['location'] = request.get('location') if request.get('location') != '其他' else request.get('location-other')
#        if result['lang-class-time'] == '6':
#            result['lang-class-time'] = '12345'
#        result['lang-class-time-other'] = request.get('lang-class-time-other')

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

        workbook = xlwt.Workbook(encoding = 'utf-8')
        sheet = workbook.add_sheet('sheet1')

        index1 = 0
        for i in ['city', 'zip', 'school_id', 'school_name', 'contact', 'phone', 'cell', 'email', 'class-time',
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
        ]:
            sheet.write(0, index1, i)
            index1 += 1

        index2 = 1
        for item in result:
            sheet.write(index2, 0, item.get('city'))
            sheet.write(index2, 1, item.get('zip'))
            sheet.write(index2, 2, item.get('school_id'))
            sheet.write(index2, 3, item.get('school_name'))
            sheet.write(index2, 4, item.get('contact'))
            sheet.write(index2, 5, item.get('phone'))
            sheet.write(index2, 6, item.get('cell'))
            sheet.write(index2, 7, item.get('email'))
            sheet.write(index2, 8, item.get('class-time'))
            index3 = 9
            for index in range(20):
                if item['lang'][index][1:4] != ["0", "0", "0"]:
                    sheet.write(index2, index3, item['lang'][index][0])
                    index3 += 1
                    sheet.write(index2, index3, '/'.join(item['lang'][index][1:4]))
                    index3 += 1

            index2 += 1

        workbook.save('school_survy.xlsx')

        request.response.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        request.response.setHeader('Content-Disposition', 'attachment; filename="school_survy.xlsx"')

        with open('school_survy.xlsx', 'r') as f:
            return f.read()


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

        workbook = xlwt.Workbook(encoding = 'utf-8')
        sheet = workbook.add_sheet('sheet1')

        index1 = 0
        for i in ['name_han', 'han_zu', 'phone', 'cell', 'city', 'zip', 'address', 'class-time', 'location',
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
        ]:
            sheet.write(0, index1, i)
            index1 += 1

        index2 = 1
        for item in result:
            sheet.write(index2, 0, item.get('name_han'))
            sheet.write(index2, 1, item.get('name_zu'))
            sheet.write(index2, 2, item.get('phone'))
            sheet.write(index2, 3, item.get('cell'))
            sheet.write(index2, 4, item.get('city'))
            sheet.write(index2, 5, item.get('zip'))
            sheet.write(index2, 6, item.get('address'))
            sheet.write(index2, 7, item.get('class-time'))
            sheet.write(index2, 8, item.get('location'))

            index3 = 9
            for index in range(20):
                if type(item['lang'][index]) == type([]):
                    sheet.write(index2, index3, item['lang'][index][0])
                    index3 += 1

                    primary = '1' if 'primary' in item['lang'][index] else '0'
                    intermediate = '1' if 'intermediate' in item['lang'][index] else '0'
                    advanced = '1' if 'advanced' in item['lang'][index] else '0'

                    sheet.write(index2, index3, '/'.join([primary, intermediate, advanced]))
                    index3 += 1

            index2 += 1
        request.response.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        request.response.setHeader('Content-Disposition', 'attachment; filename="teacher_survy.xlsx"')

        workbook.save('teacher_survy.xlsx')

        with open('teacher_survy.xlsx', 'r') as f:
            return f.read()

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

# 可上課時間採 JOSN, 方便後續媒合
        result['class-time'] = json.dumps(request.get('time'))
        result['location'] = request.get('location') if request.get('location') != '其他' else request.get('location-other')

#        result['lang-class-time'] = request.get('lang-class-time')
#        if result['lang-class-time'] == '6':
#            result['lang-class-time'] = '12345'
#        result['lang-class-time-other'] = request.get('lang-class-time-other')

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

        self.brain = api.content.find(portal_type='Course',
            context=self.portal['language_study']['latest']['class_intro'],
            sort_on='id'
        )
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

        vMeetingRoom = context.title[0:4]
        course = api.content.find(portal_type='Course', vMeetingRoom=vMeetingRoom, context=self.portal['language_study']['latest'])[0]

        # get Teacher name
        try:
            self.teacher = course.getObject().teacher.to_object.title
        except:
            self.teacher = None

        year = DateTime().year()
        month = DateTime().month()
        day = DateTime().day()
        prepareId = '%s_%s_%s' % (year, month, day)
#        import pdb; pdb.set_trace()
        try:
            self.prepare = self.portal['language_study']['latest']['class_intro'][course.id]['%s_%s' % (course.id, prepareId)]
        except:
            self.prepare = None

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



class MatchResultDownload(BrowserView):
    """ Match Result Download"""
    def __call__(self):
#        import pdb; pdb.set_trace()
        request = self.request
        result = json.loads(request.form.get('data'))


        output = StringIO()
        spamwriter = csv.writer(output)
        spamwriter.writerow(['族語教師', '上課時段', '學生數', '年級', '教學族語', '組成學校'])

        for item in result:
            row = [item.get('teacher', ' ').encode('utf-8'), item.get('classtime', ' ').encode('utf-8'), item.get('studnum', ' '),
                   item.get('level', ' ').encode('utf-8'), item.get('lang', ' ').encode('utf-8'), item.get('school', ' ').encode('utf-8')]
            spamwriter.writerow(row)

        request.response.setHeader('Content-Type', 'application/csv')
        request.response.setHeader('Content-Disposition', 'attachment; filename="match_result.csv"')

        return output.getvalue()


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
        try:
            int(can_lv) and int(req_lv)
        except:
            import pdb; pdb.set_trace()

        if int(can_lv) and int(req_lv): # 開課程度吻合
#            import pdb; pdb.set_trace()
#            if not set(school['lang-class-time']) & set(school['lang-class-time']): # 開課時間吻合
#                return

            for cTime in json.loads(teacher['class-time']):
                try:
                    # 例：詹琍敏_2_A01_primary
                    for i in range(1, 21): # 可上語別
                        if not teacher['lang%s' % i]:
                            continue
                        lang_code = teacher['lang%s' % i]
                        if not lang_code == language:
                            continue

                        for level_code in ['primary', 'intermediate', 'advanced']:
                            if not level_code == level:
                                continue
                            # 開課時間吻合，開課語系吻合，開課程度吻合，共學校數未滿，最大學生數未滿，則成立
                            if self.courseTable.has_key('%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)) and \
                               self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][2] in ['', language] and \
                               self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][1] in ['', level] and \
                               cTime in school['class-time'] and \
                               len(self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)]) < self.max_sc+2 and \
                               self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][0] < self.max_st:

                                # 檢查是否已在其它時段開課
                                already = False
                                for item in self.courseTable:
#                                    import pdb;pdb.set_trace()
                                    if [school['school_name'], language, level, int(req_lv)] in self.courseTable[item]:
                                        #print '已開'
                                        already = True
                                        break
                                if not already:
                                    # 加入共學，加計人數，確認語言，確認程度
                                    self.courseTable['%s_%s_%s_%s' %
                                        (teacher['name_han'], str(cTime), lang_code, level_code)].append(
                                            ['%s%s' % (school['city'], school['school_name']),
                                            language, level, int(req_lv)]
                                        )
                                    self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][0] += int(req_lv)
                                    self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][1] = level
                                    self.courseTable['%s_%s_%s_%s' % (teacher['name_han'], str(cTime), lang_code, level_code)][2] = language
                except:
                    print '有錯'
                    import pdb; pdb.set_trace()
                self.orderedCourseTable = OrderedDict(sorted(self.courseTable.items()))


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
#        import pdb;pdb.set_trace()

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
#            import pdb;pdb.set_trace()
            for item in json.loads(teacher['class-time']): #可上課時段
                for i in range(1, 21): # 可上語別
                    if teacher['lang%s' % i]:
                        if teacher['level%s' % i].split('/'):
                            # [學生數, 開課級別, 教學族語代號]
                            if teacher['level%s' % i].split('/')[0] == '1':
                                self.courseTable['%s_%s_%s_primary' % (teacher['name_han'], str(item), teacher['lang%s' % i])] = [0, '', '']
                            if teacher['level%s' % i].split('/')[1] == '1':
                                self.courseTable['%s_%s_%s_intermediate' % (teacher['name_han'], str(item), teacher['lang%s' % i])] = [0, '', '']
                            if teacher['level%s' % i].split('/')[2] == '1':
                                self.courseTable['%s_%s_%s_advanced' % (teacher['name_han'], str(item), teacher['lang%s' % i])] = [0, '', '']

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
#        import pdb; pdb.set_trace()
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

        data = {"description": upload_text, "topic": upload_topic}
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
        self.request.response.redirect('{}/teacher-area/gernal_login'.format(self.context.portal_url()))


class TeacherInfo(BrowserView):
    template = ViewPageTemplateFile("template/teacher_info.pt")
    def __call__(self):
        request = self.request
        portal = api.portal.get()
        teacher_uid = self.request.cookies.get("teacher_login", "")
        teacher = api.content.find(UID=teacher_uid, sort_on='getObjPositionInParent')
        if len(teacher) != 1:
            return self.request.response.redirect('{}/teacher-area/teacher-login'.format(self.context.portal_url()))
        self.teacher = teacher[0]

        # 以 respapi 執行更新族語教師個資
        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            teacherFields = ['certification', 'study', 'qualified_teacher',
                             'ethnic_teacher', 'education', 'experience', 'teaching_years',
                             'remarks', 'email', 'gender', 'nameSpell', 'aboriginalsLang']
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
            # 先 copy/paste 再 update (teacher_waiting_for_review)
            targetFolderURL = portal['teacher_waiting_for_review'].absolute_url()
            copyAction = requests.post(
                             '%s/@copy' % targetFolderURL,
                             headers={ 'Accept': 'application/json', 'Content-Type': 'application/json', },
                             json={ 'source': url, }, auth=('admin', '123456')
                         )
            if not copyAction.ok:
                api.portal.show_message(message=u'更新失敗，請稍候再試，若持續異常，請聯絡系統工程師.', request=request, type='error')[source]
                return
            url = copyAction.json()[0].get('target')
            # 以下同原動作
            response = requests.request("PATCH", url, headers=headers, json=data)
            self.context.plone_utils.addPortalMessage(u'資訊已更新，待系統審核後生效.', 'info')
            return self.request.response.redirect('{}/teacher-area/teacher-info'.format(self.context.portal_url()))
        return self.template()


class TeacherAreaSelector(BrowserView):
    template = ViewPageTemplateFile("template/teacher_area_selector.pt")
    def __call__(self):
        portal = api.portal.get()
        self.brain = api.content.find(context=portal['teacher'], portal_type="Teacher")
        return self.template()


class TeacherArea(BrowserView):
    template = ViewPageTemplateFile("template/teacher_area.pt")
    def submitLeaveClass(self, teacher):
        request = self.request

        teacherName = teacher.title
#        date = request.form.get('date')
        prepareUID = request.form.get('prepare')
        reason = request.form.get('reason')
        alertToLine = request.form.get('alert-to-line')
        alertToSchool = request.form.get('alert-to-school')
        alertToLine = '是' if alertToLine == 'true' else '否'
        alertToSchool = '是' if alertToSchool == 'true' else '否'
        note = request.form.get('note')
        teacher_uid = request.cookies.get("teacher_login", "")
        if not teacher_uid or not prepareUID:
            return

        prepare = api.content.get(UID=prepareUID)
#        teacher = api.content.get(UID=teacher_uid)

        url = '%s/edit#autotoc-item-autotoc-1' % prepare.absolute_url()

        message = """請假資訊如下
                     請假課程/日期:{}: {}
                     事由:{}
                     是否已公佈於Line群組:{}
                     是否已通知主聘學校:{}
                     調課日期時段:{}
                     請連回系統准否教師請假及後續調課作業：
                     {}""".format(prepare.getParentNode().title,
                                  prepare.start.strftime('%Y-%m-%d'), reason, alertToLine, alertToSchool, note, url)
        api.portal.send_email(
#            recipient="andersen.smartedu@gmail.com",
            recipient="andy@mingtak.com.tw",
            sender="noreply@17study.com.tw",
            subject="%s 請假單通知" % teacherName.encode('utf-8'),
            body=message,
        )
        api.portal.show_message(message=u'已送出請假單!', request=request)


    def __call__(self):
        request = self.request

        if api.user.is_anonymous():
            teacher_uid = request.cookies.get("teacher_login", "")
        else:
            teacher_uid = request.form.get('uid', '')
        self.teacher_uid = teacher_uid
        teacher = api.content.get(UID=teacher_uid)

        if not teacher:
            return self.request.response.redirect('{}/teacher-area/gernal_login'.format(self.context.portal_url()))
        self.teacher = teacher

        if request.form.has_key('submit-leave-class'):
            self.submitLeaveClass(teacher)

        return self.template()

    def getStudentData(self, uid):
        execSql = SqlObj()
        sqlStr = """SELECT name, county, school FROM student WHERE uid = '%s' AND verify = 1""" %uid
        return execSql.execSql(sqlStr)

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
        date_list = [current_time + datetime.timedelta(days=x) for x in range(0, 21)]
        courses = self.getCourse()
        prepareList = []
        self.courseList = []
        self.notPrepare = []
        self.todayPrepare = []
        for course in courses:
            prepares = api.content.find(context=course.getObject(), portal_type='Prepare', start_date=date_list, sort_on='getObjPositionInParent')
#            import pdb; pdb.set_trace()
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

    template = ViewPageTemplateFile("template/plone_root_view.pt")

    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        if request.form.has_key('live_to_schedule'):
            range = request.form.get('range')
            if range == 'latest':
                path = 'schedule'
            else:
                path = 'schedule_%s' % range
            lang = request.form.get('lang')
            request.response.redirect('%s/language_study/%s/@@course_schedule?lang=%s&range=%s' % (portal.absolute_url(), path, lang, range))
            return
        return self.template()



class CourseView(BrowserView):

    template = ViewPageTemplateFile("template/course_view.pt")

    def __call__(self):
        context = self.context
        request = self.request

        self.school_uid = False
        self.schoolTitle = ''
        self.loginUser = False
        if api.user.is_anonymous():
            self.school_uid = request.cookies.get("school_login", "")
        else:
            self.loginUser = True

        if not self.loginUser and self.school_uid:
            self.schoolTitle = api.content.get(UID=self.school_uid).title

        courses = context.getChildNodes()
        self.items = []
        for item in courses:
            if item.embeded and not self.items:
                self.items.append(item)
            elif self.items:
                self.items.append(item)
        for item in courses:
            if not item.embeded:
                self.items.append(item)
            else:
                break
        return self.template()


class CourseStudent(BrowserView):
    def getStudents(self):
        portal = api.portal.get()
        request = self.request

        folder = request.form.get('folder', 'latest')
        courses = api.content.find(portal_type="Course", context=portal['language_study'][folder]['class_intro'])
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
            execSql = SqlObj()
            sqlStr = """SELECT * FROM student WHERE uid = '{}' AND verify = 1""".format(context.getParentNode().UID())
            self.studentData = execSql.execSql(sqlStr)
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

        on_call = request.form.get('on_call').split('||')
        not_on_call = request.form.get('not_on_call').split('||')

        course = context.getParentNode().title.encode('utf-8')

        id = context.id.split('_')
        date = '%s-%s-%s' %(id[1], id[2], id[3])
        uid = context.UID()

        execSql = SqlObj()

        sqlStr = """DELETE FROM attend WHERE uid = '{}'""".format(uid)
        execSql.execSql(sqlStr)

        for i in on_call:
            if not i:
                continue
            temp = i.split(',')
            name = temp[2].split('(')[0]
            sqlStr = """INSERT INTO attend(name, date, course, county, school, uid, status) VALUES('{}', '{}', '{}', '{}', '{}', '{}', 'onCall')
                     """.format(name, date, course, temp[0], temp[1], uid)
            execSql.execSql(sqlStr)

        for i in not_on_call:
            if not i:
                continue
            temp = i.split(',')
            name = temp[2].split('(')[0]

            sqlStr = """INSERT INTO attend(name, date, course, county, school, uid, status) VALUES('{}', '{}', '{}', '{}', '{}', '{}', 'notOnCall')
                     """.format(name, date, course, temp[0], temp[1], uid)
            execSql.execSql(sqlStr)


        return 
        # email
        for item in context.notOnCall.split('\n'):
            if not item:
                continue
#            import pdb;pdb.set_trace()
            cityTitle, schoolName, name = item.split(',')
            city = api.content.find(path='/apc_costudy/school', Title=cityTitle, depth=1)[0]
            school = api.content.find(path=city.getPath(), Title=schoolName)[0]
            email = school.getObject().email
            # 寄 Email
            try:
                api.portal.send_email(
                    recipient=email,
                    sender="noreply@17study.com.tw",
                    subject="原住民族語直播共學平台系統通知: 學生點名未到課",
                    body="共學組: {}\n課堂日期:{}\n點名未到學生: {}".format(context.getParentNode().title.encode('utf-8'),
                          context.title.encode('utf-8'), item),
                )
            except:
                pass
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
        self.request.response.redirect('{}/school-area/gernal_login'.format(self.context.portal_url()))


class SchoolAreaSelector(BrowserView):
    template = ViewPageTemplateFile("template/school_area_selector.pt")
    def __call__(self):
        self.brain = api.content.find(portal_type="School", sort_on="id")
        return self.template()


class SchoolArea(BrowserView):
    template = ViewPageTemplateFile("template/school_area.pt")
    def __call__(self):
        request = self.request
        portal = api.portal.get()

        if api.user.is_anonymous():
            school_uid = request.cookies.get("school_login", "")
        else:
            school_uid = request.form.get('uid', '')

        self.school_uid = school_uid
        school = api.content.get(UID=school_uid)

        if not school:
            return self.request.response.redirect('{}/school-area/gernal_login'.format(self.context.portal_url()))
        self.school = school

        if request.get("widget-form-btn", "") == "widget-email-form":
            self.updateEmail()
            return request.response.redirect('%s/school/@@school_area?uid=%s' % (portal.absolute_url(), school_uid))

        if request.get("widget-form-btn", "") == "widget-namelist-form":
            self.updateNamelist()
            return request.response.redirect('%s/school/@@school_area?uid=%s' % (portal.absolute_url(), school_uid))

        if request.get("widget-form-btn", "") == "widget-addStudent-form":
            self.addStudent()
            return request.response.redirect('%s/school/@@school_area?uid=%s' % (portal.absolute_url(), school_uid))\

        return self.template()

    def getPathname(self):
        cookie_path = api.portal.get().absolute_url_path()
        return cookie_path

    def getCourse(self):
        school_uid = self.school.UID()
        portal = api.portal.get()

        course = api.content.find(portal_type='Course', course_schools=school_uid, context=portal['language_study']['latest']['class_intro'])
        return course

    def getStudentData(self, uid):
        execSql = SqlObj()
        school = self.school.Title()
        sqlStr = """SELECT name, verify, level FROM student WHERE uid = '%s' AND school = '%s' and cancel = 0""" %(uid, school)
        data = execSql.execSql(sqlStr)
        return data

    def addStudent(self):
        request = self.request
        course_uid = request.get('course_uid')
        student = request.get('student')
        course = request.get('course')
        language = request.get('language')
        level = request.get('level')
        school = self.school.title.encode('utf-8')
        county = self.school.getParentNode().title.encode('utf-8')

        execSql = SqlObj()
        sqlStr = """INSERT INTO student(school, course, language, name, uid, county, level) VALUES('{}', '{}', '{}', '{}', '{}', '{}', {})
                 """.format(school, course, language, student, course_uid, county, level)
        execSql.execSql(sqlStr)


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


class SchoolAreaEdit(SchoolArea):
    template = ViewPageTemplateFile("template/school_area_edit.pt")


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

    template = ViewPageTemplateFile("template/course_schedule_2.pt")

    def getWeekDay(self, id):
        try:
            year = int(id.split('_')[1])
            month = int(id.split('_')[2])
            day = int(id.split('_')[3])
            return datetime.datetime(year, month, day).strftime('%w')
        except:
            pass
#            import  pdb; pdb.set_trace()

    def getCourse(self, timeSection):
        context = self.context
        request = self.request
        portal = api.portal.get()
        range = request.form.get('range', 'latest')
        brain = api.content.find(timeSection=timeSection, context=self.portal['language_study'][range], sort_on='id')
        return brain

    def __call__(self):
        context = self.context
        request = self.request
        self.portal = api.portal.get()

#        range = request.form.get('range', 'latest')
#        self.brain = api.content.find(context=self.portal['language_study'][range], portal_type='Course', sort_on='id')
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


class MatchResult2(MatchResult):
    """ Match Result2 """
    template = ViewPageTemplateFile("template/match_result2.pt")
