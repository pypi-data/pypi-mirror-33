from django import template
from googletrans import Translator as T
from ..models import gTranslation


register = template.Library()
s_languages = [
    'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 
    'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs',
    'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl',
    'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'he',
    'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km',
    'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms',
    'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'ps', 'fa', 'pl',
    'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si',
    'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th',
    'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu', 'fil'
]


@register.simple_tag
def gtranslate(text='translate !', dest='fr', src='en', cache=False):
    """
        Template custom tag to fetch google translation with
        Googletrans and cache it, If enabled.
        @param: text inputted text to be translated (Default: 'translate !')
        @param: dest list of languages to translate to (Default: 'fr')
        @param: src language to translate from (Default: 'en')
        @param: cache to enable caching into gt_cache.json (Default: False)
    """
    for att in ['text', 'src', 'dest']:
        if not isinstance(eval(att), str):
            raise(AttributeError(
                'gtranslate(' + att + ') takes a string'
            ))
    if src not in s_languages:
        raise(AttributeError(
            'gtranslate(src=' + src + ') language is not supported'
        ))
    if dest not in s_languages:
        raise(AttributeError(
            'gtranslate(dest=' + dest + ') language is not supported'
        ))
    if cache:
        for gTran in gTranslation.objects.all().filter(text=text, language=dest):
            return gTran.translation
    gTran = T().translate(text, dest, src).text
    if cache:
        gTranslation(text=text, language=dest, translation=gTran).save()
    return gTran