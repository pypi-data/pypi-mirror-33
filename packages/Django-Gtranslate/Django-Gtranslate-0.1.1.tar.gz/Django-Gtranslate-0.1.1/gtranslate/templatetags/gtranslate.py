from django import template
from googletrans import Translator as T
from os.path import isfile
from json import dumps, load


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

def getCache(f_path='gt_cache.json'):
    """
    function to try loading cache file and return it
    """
    try:
        with open(f_path, 'r+') as file:
            return load(file)
    except Exception:
        raise(IOError('gtranslate(cache=True) failed to load cached file.'))


def cacheIt(inp_var, f_path='gt_cache.json'):
    """
    function to overwrite the cached translation file
    """
    with open(f_path, 'w+') as file:
        file.write(dumps(
            inp_var, indent=4, separators=(',', ': '), sort_keys=True
        ))


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
    # return T().translate(text, dest, src).text
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
    t = T()
    if cache:
        if isfile('gt_cache.json'):
            data = getCache()
            if text in data.keys():
                if dest not in data[text].keys():
                    data[text][dest] = t.translate(text, dest, src).text
            else:
                data[text] = {dest: t.translate(text, dest, src).text}
            cacheIt(data)
            return data[text][dest]
        else:
            translation = t.translate(text, dest, src).text
            cacheIt({text: {dest: translation}})
            return translation
    else:
        return t.translate(text, dest, src).text