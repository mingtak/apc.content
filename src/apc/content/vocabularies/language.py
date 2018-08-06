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
class Language(object):
    """
    """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        items = [
            VocabItem(u'1', u'A00.阿美族語(不分方言別)'),
            VocabItem(u'2', u'A01.北部阿美語'),
            VocabItem(u'3', u'A02.中部阿美語'),
            VocabItem(u'4', u'A03.海岸阿美語'),
            VocabItem(u'5', u'A04.馬蘭阿美語 '),
            VocabItem(u'6', u'A05.恆春阿美語'),
            VocabItem(u'7', u'B00.泰雅族語(不分方言別)'),
            VocabItem(u'8', u'B06.賽考利克泰雅語'),
            VocabItem(u'9', u'B07.澤敖利泰雅語'),
            VocabItem(u'10', u'B08.汶水泰雅語'),
            VocabItem(u'11', u'B09.萬大泰雅語'),
            VocabItem(u'12', u'B10.四季泰雅語'),
            VocabItem(u'13', u'B11.宜蘭澤敖利泰雅語'),
            VocabItem(u'14', u'C00.排灣族語(不分方言別)'),
            VocabItem(u'15', u'C12.東排灣語'),
            VocabItem(u'16', u'C13.北排灣語'),
            VocabItem(u'17', u'C14.中排灣語'),
            VocabItem(u'18', u'C15.南排灣語'),
            VocabItem(u'19', u'D00.布農族語(不分方言別)'),
            VocabItem(u'20', u'D16.卓群布農語'),
            VocabItem(u'21', u'D17.卡群布農語'),
            VocabItem(u'22', u'D18.丹群布農語'),
            VocabItem(u'23', u'D19.巒群布農語'),
            VocabItem(u'24', u'D20.郡群布農語'),
            VocabItem(u'25', u'E00.卑南族(不分方言別)'),
            VocabItem(u'26', u'E21.南王卑南語'),
            VocabItem(u'27', u'E22.知本卑南語'),
            VocabItem(u'28', u'E23.初鹿卑南語'),
            VocabItem(u'29', u'E24.建和卑南語'),
            VocabItem(u'30', u'F00.魯凱族語(不分方言別)'),
            VocabItem(u'31', u'F25.東魯凱語'),
            VocabItem(u'32', u'F26.霧台魯凱語'),
            VocabItem(u'33', u'G31.鄒語'),
            VocabItem(u'34', u'H32.卡那卡那富語'),
            VocabItem(u'35', u'J34.賽夏語'),
            VocabItem(u'36', u'K35.雅美語'),
            VocabItem(u'37', u'L36.邵語'),
            VocabItem(u'38', u'M37.噶瑪蘭語'),
            VocabItem(u'39', u'N38.太魯閣語'),
            VocabItem(u'40', u'P00.賽德克族語(不分方言別)'),
            VocabItem(u'41', u'P40.都達語'),
            VocabItem(u'42', u'P41.德固達雅語'),
            VocabItem(u'43', u'P42.德魯固語'),
            VocabItem(u'44', u'Q43.噶哈巫語'),
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


LanguageFactory = Language()
