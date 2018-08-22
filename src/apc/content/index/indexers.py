#!/usr/bin/python
# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer
from plone.app.contenttypes.interfaces import INewsItem
from apc.content.content.course import ICourse
import hashlib


@indexer(ICourse)
def hashSHA256(obj):
    uid = obj.UID()
    return hashlib.sha256(uid).hexdigest()
