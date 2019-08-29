# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from z3c.relationfield.relation import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds

import logging
import requests
import json
import sys
import datetime
import csv

logger = logging.getLogger("apc.content")


class AddCourse1081(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        context = self.context
        request = self.request
        intIds = component.getUtility(IIntIds)

        with open('/home/andy/course_datetime_108_1.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course_id = row['共學組'][0:8]
                start = row['初堂課時間']
                course_name = row['共學組'][8:]
                meeting_room = row['共學組'][4:8]
                timeSection = row['上課時段']

                teacher = row['授課教師'].strip()
                mainSchool = row['主辦學校'].strip()
                schools = row['組成學校'].strip().split('\n')

                year = int(start[0:4])
                month = int(start[4:6])
                day = int(start[6:8])
                hour = int(start[8:10]) - 8
                minute = int(start[10:])

                date = datetime.datetime(year, month, day, hour, minute)

                # 建course
                courseTitle = row['共學組']
# 二段式，下面 " " " 拿掉，可以建course, 加上去可以建prepare
                """
                # 先找teacher
                teacherBrain = None
                if teacher:
                    teacherBrain = api.content.find(portal_type='Teacher', Title=safe_unicode(teacher)[0:3])
                    if teacherBrain:
                        logger.info(teacherBrain[0].Title)
                        teacher = teacherBrain[0].getObject()
                    else:
                        import pdb; pdb.set_trace()

                # 再找school
                schoolResult = []
                mainSchoolResult = None
                first = True
                for item in schools:
                    city = safe_unicode(item)[0:3]
                    sName = safe_unicode(item)[3:]
                    try:
                        schoolBrain = api.content.find(portal_type='School', Title=sName)
                    except:
                        try:
                            schoolBrain = api.content.find(portal_type='School', Title=safe_unicode(item)[3:8])
                        except:
                            import pdb;pdb.set_trace()

                    if len(schoolBrain) == 1:
                        schoolResult.append( RelationValue( intIds.getId( schoolBrain[0].getObject() ) ) )
                        if first == True:
                            mainSchoolResult = RelationValue( intIds.getId( schoolBrain[0].getObject() ) )
                            first = False
                    elif len(schoolBrain) > 1:
                        pTitle = ''
                        for item2 in schoolBrain:
                            pTitle = item2.getObject().getParentNode().title
                            if pTitle == city:
                                schoolResult.append( RelationValue( intIds.getId( item2.getObject() ) ) )
                                if first == True:
                                    mainSchoolResult = RelationValue( intIds.getId( schoolBrain[0].getObject() ) )
                                    first = False
                        if not pTitle:
                            logger.error('No pTitle')
                            import pdb; pdb.set_trace()
                    else:
                        logger.error('No schoolBrain')
                        import pdb; pdb.set_trace()

                print (schoolResult)

                obj = api.content.create(container=portal['language_study']['latest']['class_intro'],
                                         type='Course',
                                         id=course_id,
                                         title=courseTitle,
                                         vMeetingRoom=meeting_room,
                                         timeSection=timeSection,
                                         local_language=course_name,
                                         teacher=RelationValue(intIds.getId(teacher)) if teacherBrain else None,
                                         school = schoolResult if schoolResult else None,
                                         hire_school = mainSchoolResult if mainSchoolResult else None,
                )

                continue
                """

                # 建每周備課
                for i in range(22):
                    year = date.year
                    month = date.month
                    day = date.day

                    contentId = '%s_%s_%s_%s' % (course_id, year, month, day)
                    title = '%s月%s日' % (month, day)

                    resp = requests.post('http://apc2.17study.com.tw/language_study/latest/class_intro/%s' % course_id,
                               headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                               json={'@type': 'Prepare',
                                     'title': title,
                                     'id':contentId,
                                     'start':'%s-%s-%s %s:%s' % (date.year, date.month, date.day, date.hour, date.minute),
                                     'end':'%s-%s-%s %s:%s' % (date.year, date.month, date.day, date.hour+1, date.minute),
                               },
                               auth=('admin', '123456'))
                    logger.info('%s: %s' % (contentId, resp.status_code))
                    if not resp.ok:
                        import pdb; pdb.set_trace()
                    date += datetime.timedelta(days = 7)
#                break

