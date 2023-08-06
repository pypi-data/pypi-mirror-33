from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .templatetags.gtranslate import gtranslate
# Create your views here.

def gTranslate(r, src='en', dest='fr', text='translation'):
    """ 
    To return json dynamic translation response :
    {translation : 'translated text ...'}
    @param: src language to translate from (default: 'en')
    @param: dest language to translate to (default: 'fr')
    @param: text text to be translated (default: 'translation')
    """
    return JsonResponse(
        {'translation': 
        gtranslate(
            text=text,
            src=src,
            dest=dest,
            cache=True
        ).replace('%5C', '/')}
    )


@login_required
def gTranslateAuth(r, src, dest, text):
    """ 
    To return json dynamic translation response only for authenticated :
    {translation : 'translated text ...'}
    @param: src language to translate from (default: 'en')
    @param: dest language to translate to (default: 'fr')
    @param: text text to be translated (default: 'translation')
    """
    return JsonResponse(
        {'translation': 
        gtranslate(
            text=text,
            src=src,
            dest=dest,
            cache=True
        ).replace('%5C', '/')}
    )