# -*- coding: utf-8 -*-
from apc.content import _
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from mingtak.ECBase.browser.views import SqlObj
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from bs4 import BeautifulSoup as bs
import json


class FullscreenYoutube(BrowserView):
    template = ViewPageTemplateFile('template/fullscreen_youtube.pt')
    def __call__(self):
        request = self.request
        id = request.get('id')
        execSql = SqlObj()
        sqlStr = """SELECT embedUrl FROM youtube WHERE id = '%s'""" %id
        self.result = execSql.execSql(sqlStr)
        return self.template()


class AnalysisYoutube(BrowserView):
    template = ViewPageTemplateFile('template/analysis_youtube.pt')
    template2 = ViewPageTemplateFile('template/result_youtube.pt')
    def __call__(self):
        request = self.request
        keyword = request.get('keyword')
        language = request.get('language')

        if keyword or language:
            execSql = SqlObj()
            if keyword and language:
                sqlStr = """SELECT * FROM youtube WHERE keyword LIKE '%%{}%%' AND language LIKE '%%{}%%'""".format(keyword, language)
            elif keyword:
                sqlStr = """SELECT * FROM youtube WHERE keyword LIKE '%%{}%%'""".format(keyword)
            elif language:
                sqlStr = """SELECT * FROM youtube WHERE language LIKE '%%{}%%'""".format(language)
            else:
                self.result = []
                return self.template2()

            self.result = execSql.execSql(sqlStr)
            return self.template2()
        else:
            return self.template()


class FetchYoutube(BrowserView):
    def __call__(self):
        # 抓影片右邊的影片列表, 會一次顯示所有影片
#        url = 'https://www.youtube.com/watch?v=Blh4fv2LXpg&list=PLBTGDa1tS7xFyMJMgbQuUsy5FzoRc65aB'
        url = 'https://www.youtube.com/watch?v=i7ScDVyN56I&list=PLmP3ukJ2_C1aXYr-DnjeFb-v176PreCIb&index=2&t=0s'

        playlist = requests.get(url)
        soup = bs(playlist.text, 'html.parser')

        portal = api.portal.get()
        execSql = SqlObj()
        alsoProvides(self.request, IDisableCSRFProtection)

        # 抓playlist 裡的影片
        # TODO 反轉playlist抓後十個
        for i in soup.select('.playlist-video'):
            href = i.get('href')
            # 抓影片資料
            video = requests.get('https://www.youtube.com%s' %href)

            soup2 = bs(video.text, 'html.parser')
#            title = soup2.select('#eow-title')[0].text.strip()

            description = soup2.select('#eow-description')[0].text
            if not description:
                continue
            title = description.split(',')[0]

            videoId = video.url.split('v=')[1].split('&list')[0]
            courseId = title.split('-')[0].split('_')[0]
            prepareId = title.split('-')[0]
            language = title.split('-')[1]

            sqlStr = """SELECT id FROM `youtube` WHERE videoId = '{}'""".format(videoId)
            check = execSql.execSql(sqlStr)
            # 確認是否重複
            if check:
                continue

            content = portal['language_study']['108test']['class_intro'][courseId][prepareId]

            embedUrl = """<iframe width='560' height='315' src='https://www.youtube.com/embed/%s' frameborder='0'
                          allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'
                          allowfullscreen></iframe>""" %(videoId)
            content.embeded = embedUrl
#            content.cover_url = cover_url

            # 分析說明
            if description:
                for desc in description.split(',')[1:]:
                    if desc:
                        temp = desc.split('-')
                        timeList = temp[0].split(':')

                        # 計算影片起始時間
                        if len(timeList) == 3:
                            time =  int(timeList[0])*60*60 + int(timeList[1])*60 + int(timeList[2])
                        elif len(timeList) == 2:
                            time = int(timeList[0])*60 + int(timeList[1])
                        else:
                            continue

                        keyword = temp[1]
                        embedUrl = """<iframe width='560' height='315' src='https://www.youtube.com/embed/%s?start=%s' frameborder='0'
                              allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'
                              allowfullscreen></iframe>""" %(videoId, time)

                        sqlStr = """INSERT INTO youtube(keyword, time, embedUrl, videoId, language) VALUES("{}", {}, "{}", "{}", "{}")
                             """.format(keyword, time, embedUrl, videoId, language)
                        try:
                            execSql.execSql(sqlStr)
                        except:
                            import pdb;pdb.set_trace()

#已無用
class UploadYoutube(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        content = api.content.find(context=portal['language_study'], Type='Prepare')

        collect = []
        for brain in content:
            if len(collect) == 3:
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

#已無用
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
