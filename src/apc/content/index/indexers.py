#!/usr/bin/python
# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer
from plone.app.contenttypes.interfaces import INewsItem
from apc.content.content.teacher import ITeacher
from apc.content.content.school import ISchool
from apc.content.content.course import ICourse
from apc.content.content.prepare import IPrepare
import hashlib


@indexer(ICourse)
def vMeetingRoom(obj):
    return obj.vMeetingRoom

@indexer(ICourse)
def courseTeacher(obj):
    uid = obj.teacher.to_object.UID
    return uid

@indexer(ICourse)
def courseSchools(obj):
    if obj.school:
        schools = [school.to_object.UID() for school in obj.school]
        return schools

@indexer(IPrepare)
def start_date(obj):
    date = obj.start.date()
    return date

@indexer(ITeacher)
def hashSHA256_teacher(obj):
    uid = obj.UID()
    return hashlib.sha256(uid).hexdigest()

@indexer(ITeacher)
def teacherID(obj):
    teacher_id = obj.teacher_id
    return teacher_id

@indexer(ISchool)
def hashSHA256_school(obj):
    uid = obj.UID()
    return hashlib.sha256(uid).hexdigest()

@indexer(ISchool)
def schoolID(obj):
    school_id = obj.school_id
    return school_id
