# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import os
import requests


class UploadYoutube(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        content = api.content.find(context=portal['language_study'], Type='Prepare')

        collect = []
        for brain in content:
            if len(collect) == 5:
                break
            obj = brain.getObject()
            download_url = obj.download_url
            if download_url and not obj.youtube_embeded:
                parent = obj.getParentNode()
                title = parent.title.split(parent.id)[1]
                fileName = '%s-%s.mp4' %(obj.id, title)
                if not os.path.isfile('/home/andy/apc/zeocluster/%s' %fileName):
                    file = requests.get(download_url)

                    with open(fileName, 'wb') as f:
                        f.write(file.content)
                collect.append(fileName)
                os.system('python upload_youtube.py --file %s --title %s --uid %s' %(fileName, fileName.split('.')[0], obj.UID()))


class UpdateYoutubeEmbeded(BrowserView):
    def __call__(self):
        request = self.request
        uid = request.get('uid')
        youtube_id = request.get('youtube_id')
        content = api.content.get(UID=uid)

        embedUrl = """<iframe width='560' height='315' src='https://www.youtube.com/embed/%s' frameborder='0'
                      allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'
                      allowfullscreen></iframe>""" %(youtube_id)

        content.youtube_embeded = embedUrl
        parent = content.getParentNode()
        fileName = '%s-%s.mp4' %(content.id, parent.title.split(parent.id)[1])
        os.system('rm %s' %fileName)
