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
            VocabItem(u'1', u'周一/早自習'),
            VocabItem(u'2', u'周二/早自習'),
            VocabItem(u'3', u'周三/早自習'),
            VocabItem(u'4', u'周四/早自習'),
            VocabItem(u'5', u'周五/早自習'),
            VocabItem(u'6', u'周一/第1節'),
            VocabItem(u'7', u'周二/第1節'),
            VocabItem(u'8', u'周三/第1節'),
            VocabItem(u'9', u'周四/第1節'),
            VocabItem(u'10', u'周五/第1節'),
            VocabItem(u'11', u'周一/第2節'),
            VocabItem(u'12', u'周二/第2節'),
            VocabItem(u'13', u'周三/第2節'),
            VocabItem(u'14', u'周四/第2節'),
            VocabItem(u'15', u'周五/第2節'),
            VocabItem(u'16', u'周一/第3節'),
            VocabItem(u'17', u'周二/第3節'),
            VocabItem(u'18', u'周三/第3節'),
            VocabItem(u'19', u'周四/第3節'),
            VocabItem(u'20', u'周五/第3節'),
            VocabItem(u'21', u'周一/第4節'),
            VocabItem(u'22', u'周二/第4節'),
            VocabItem(u'23', u'周三/第4節'),
            VocabItem(u'24', u'周四/第4節'),
            VocabItem(u'25', u'周五/第4節'),
            VocabItem(u'26', u'周一/午休'),
            VocabItem(u'27', u'周二/午休'),
            VocabItem(u'28', u'周三/午休'),
            VocabItem(u'29', u'周四/午休'),
            VocabItem(u'30', u'周五/午休'),
            VocabItem(u'31', u'周一/第5節'),
            VocabItem(u'32', u'周二/第5節'),
            VocabItem(u'33', u'周三/第5節'),
            VocabItem(u'34', u'周四/第5節'),
            VocabItem(u'35', u'周五/第5節'),
            VocabItem(u'36', u'周一/第6節'),
            VocabItem(u'37', u'周二/第6節'),
            VocabItem(u'38', u'周三/第6節'),
            VocabItem(u'39', u'周四/第6節'),
            VocabItem(u'40', u'周五/第6節'),
            VocabItem(u'41', u'周一/第7節'),
            VocabItem(u'42', u'周二/第7節'),
            VocabItem(u'43', u'周三/第7節'),
            VocabItem(u'44', u'周四/第7節'),
            VocabItem(u'45', u'周五/第7節'),
            VocabItem(u'46', u'周一/第8節'),
            VocabItem(u'47', u'周二/第8節'),
            VocabItem(u'48', u'周三/第8節'),
            VocabItem(u'49', u'周四/第8節'),
            VocabItem(u'50', u'周五/第8節'),
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
