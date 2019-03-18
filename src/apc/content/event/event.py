# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.utils import safe_unicode
from apc.content import _

import datetime


def updateDate(obj, event):
    course = obj.id.split('_')[0]
    year = obj.id.split('_')[1]
    month = obj.title.split(safe_unicode('月'))[0]
    day = obj.title.split(safe_unicode('月'))[1].split(safe_unicode('日'))[0]
    tzinfo = obj.start.tzinfo

    newId = '%s_%s_%s_%s' % (course, year, month, day)
    if newId == obj.id:
        return

    obj.start = datetime.datetime(int(year), int(month), int(day), 8, 0, tzinfo=tzinfo)
    obj.end = datetime.datetime(int(year), int(month), int(day), 9, 0, tzinfo=tzinfo)

    api.content.rename(obj=obj, new_id=newId, safe_id=True)
    obj.reindexObject()


def moveObjectsToTop(obj, event):
    """
    Moves Items to the top of its folder
    """
    folder = obj.getParentNode()
    if folder != None and hasattr(folder, 'moveObjectsToTop'):
        folder.moveObjectsToTop(obj.id)
