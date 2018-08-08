# -*- coding: utf-8 -*-

# from plone import api
from apc.content import _
from plone.dexterity.interfaces import IDexterityContent
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class VocabItem(object):
    def __init__(self, token, value):
        self.token = token
        self.value = value


@implementer(IVocabularyFactory)
class ClassTime(object):
    """
    """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        items = [
            VocabItem(u'1-1', u'周一/早自習'),
            VocabItem(u'2-1', u'周二/早自習'),
            VocabItem(u'3-1', u'周三/早自習'),
            VocabItem(u'4-1', u'周四/早自習'),
            VocabItem(u'5-1', u'周五/早自習'),
            VocabItem(u'1-2', u'周一/第1節'),
            VocabItem(u'2-2', u'周二/第1節'),
            VocabItem(u'3-2', u'周三/第1節'),
            VocabItem(u'4-2', u'周四/第1節'),
            VocabItem(u'5-2', u'周五/第1節'),
            VocabItem(u'1-3', u'周一/第2節'),
            VocabItem(u'2-3', u'周二/第2節'),
            VocabItem(u'3-3', u'周三/第2節'),
            VocabItem(u'4-3', u'周四/第2節'),
            VocabItem(u'5-3', u'周五/第2節'),
            VocabItem(u'1-4', u'周一/第3節'),
            VocabItem(u'2-4', u'周二/第3節'),
            VocabItem(u'3-4', u'周三/第3節'),
            VocabItem(u'4-4', u'周四/第3節'),
            VocabItem(u'5-4', u'周五/第3節'),
            VocabItem(u'1-5', u'周一/第4節'),
            VocabItem(u'2-5', u'周二/第4節'),
            VocabItem(u'3-5', u'周三/第4節'),
            VocabItem(u'4-5', u'周四/第4節'),
            VocabItem(u'5-5', u'周五/第4節'),
            VocabItem(u'1-6', u'周一/午休'),
            VocabItem(u'2-6', u'周二/午休'),
            VocabItem(u'3-6', u'周三/午休'),
            VocabItem(u'4-6', u'周四/午休'),
            VocabItem(u'5-6', u'周五/午休'),
            VocabItem(u'1-7', u'周一/第5節'),
            VocabItem(u'2-7', u'周二/第5節'),
            VocabItem(u'3-7', u'周三/第5節'),
            VocabItem(u'4-7', u'周四/第5節'),
            VocabItem(u'5-7', u'周五/第5節'),
            VocabItem(u'1-8', u'周一/第6節'),
            VocabItem(u'2-8', u'周二/第6節'),
            VocabItem(u'3-8', u'周三/第6節'),
            VocabItem(u'4-8', u'周四/第6節'),
            VocabItem(u'5-8', u'周五/第6節'),
            VocabItem(u'1-9', u'周一/第7節'),
            VocabItem(u'2-9', u'周二/第7節'),
            VocabItem(u'3-9', u'周三/第7節'),
            VocabItem(u'4-9', u'周四/第7節'),
            VocabItem(u'5-9', u'周五/第7節'),
            VocabItem(u'1-10', u'周一/第8節'),
            VocabItem(u'2-10', u'周二/第8節'),
            VocabItem(u'3-10', u'周三/第8節'),
            VocabItem(u'4-10', u'周四/第8節'),
            VocabItem(u'5-10', u'周五/第8節'),
        ]

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        # create a list of SimpleTerm items:
        terms = []
        for item in items:
            terms.append(
                SimpleTerm(
                    value=item.token,
                    token=str(item.token),
                    title=item.value,
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


ClassTimeFactory = ClassTime()
