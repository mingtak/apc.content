# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from mingtak.ECBase.browser.views import SqlObj
import datetime


class DetectNotRollCall(BrowserView):
    def __call__(self):
        request = self.request
        portal = api.portal.get()
        execSql = SqlObj()

        now = datetime.datetime.now()

        prepareList = api.content.find(context=portal['language_study'], portal_type='Prepare',
                      start_date = {'query': (datetime.date(now.year, now.month, now.day), datetime.date(now.year, now.month, now.day))
                                   , 'range': 'min: max'})
#        prepareList = [api.content.get(UID='e9a28fd812014e849e5f4868168e3f4a')]

        for brain in prepareList:
            obj = brain.getObject()
#        for obj in prepareList:

            uid = obj.UID()
            sqlStr = "SELECT name FROM attend WHERE uid = '{}'".format(uid)
            attend = execSql.execSql(sqlStr)
            attend = [i[0] for i in attend]

            parentUid = obj.getParentNode().UID()
            sqlStr = "SELECT * FROM student WHERE uid = '{}' AND verify = 1".format(parentUid)
            student = execSql.execSql(sqlStr)

            date = now.strftime('%Y-%m-%d')
            for item in student:
                temp = dict(item)
                name = temp['name']
                county = temp['county']
                school = temp['school']
                course = '%s%s' %(temp['course'], temp['language'])

                if name not in attend:
                    sqlStr = """INSERT INTO attend(name, date, status, course, county, school, uid) VALUES('{}', '{}', '{}', '{}', '{}',
                            '{}', '{}')""".format(name, date, 'notOnCall', course, county, school, uid)
                    execSql.execSql(sqlStr)
