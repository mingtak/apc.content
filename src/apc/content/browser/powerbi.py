# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from Products.CMFPlone.utils import safe_unicode
import logging
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
import adal
from pypowerbi.dataset import Column, Table, Dataset
from pypowerbi.client import PowerBIClient

import sys
reload(sys)
sys.setdefaultencoding('utf8')


logger = logging.getLogger("apc.content")



class ShowPieChart(BrowserView):
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
            count = {'到課': 0, '缺課': 0}

            start = request.get('start')
            end = request.get('end')
            month = request.get('month')

            sqlStr = """SELECT COUNT(status) FROM attend WHERE date """

            if start and end:
                onCallStr = """BETWEEN '{}' AND '{}' AND status = 'onCall'""".format(start, end)
                notOnCallStr = """BETWEEN '{}' AND '{}' AND status = 'notOnCall'""".format(start, end)
            elif month:
                onCallStr = """like '{}' AND status = 'onCall'""".format(month + '%%')
                notOnCallStr = """like '{}' AND status = 'notOnCall'""".format(month + '%%')


            onCall = execSql.execSql('%s %s' %(sqlStr, onCallStr))[0][0]
            notOnCall = execSql.execSql('%s %s' %(sqlStr, notOnCallStr))[0][0]

            self.start = start
            self.end = end
            self.month = month
            self.result = json.dumps({'onCall': onCall, 'notOnCall': notOnCall})
            return self.template3()

        elif mode == 'notOnCallDetail':
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
        password = 'password' #假，資料移轉時請改輸入正確密碼，或由下一家提供

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
