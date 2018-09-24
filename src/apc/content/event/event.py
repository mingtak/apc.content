# -*- coding: utf-8 -*-
from plone import api
from apc.content import _


def moveObjectsToTop(obj, event):
    """
    Moves Items to the top of its folder
    """
    folder = obj.getParentNode()
    if folder != None and hasattr(folder, 'moveObjectsToTop'):
        folder.moveObjectsToTop(obj.id)
