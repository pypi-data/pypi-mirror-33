<h1 align='center'> django_gtranslate </h1>
<p align='center'>
<a href="https://travis-ci.com/mrf345/django_gtranslate"><img src="https://travis-ci.com/mrf345/django_gtranslate.svg?branch=master" /></a>
<a href='https://coveralls.io/github/mrf345/django_gtranslate?branch=master'><img src='https://coveralls.io/repos/github/mrf345/django_gtranslate/badge.svg?branch=master' alt='Coverage Status' /></a>
</p>
<h3 align='center'>
    A Django app to add google translation to the template and
    adds view for dynamic translation, finally stores it in the database 
</h3>

## Install:

#### - With pip
> - `pip install Django-Gtranslate` <br />

#### - From the source:
> - `git clone https://github.com/mrf345/django_gtranslate.git`<br />
> - `cd django_gtranslate` <br />
> - `python setup.py install`

## Setup:
#### - Add it to the `settings.py` in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    'gtranslate',
    ...
]
```
> After adding the app make sure to do migration for caching model :
> - `python manage.py makemigrations gtranslate`
> - `python manage.py migrate gtranslate`

#### - Inside jinja template:
```jinja
{% load gtranslate %}
<h1>{% gtranslate 'text to translate' 'fr' %}</h1>
```

#### - To add a dynamic translation view to `urls.py`: 
```python
from django.urls import path, include

urlpatterns = [
    ...
    # for unauthorized access dynamic translation 
    path('gtran/', include('gtranslate.urls')),
    # for user authorized dynamic translation
    path('gtran/', include('gtranslate.urls_auth')),
    ...
]
```
> now you can access `http://localhost:8000/<src>/<dest>/<text>` and, it should return json response `{'translation': 'translated text'}`

####

## - Options:
```python
def gtranslate(
        text='translation !', # Text to be translated
        dest='fr', # Language to translate to
        src='en', # Language to be translated from
        cache=False, # To store and restore the translation in and from the database
        ): 
```


#### - List of supported languages:
`{
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
    'fil': 'Filipino',
    'he': 'Hebrew'
}`

## Credit:
> - [Googletrans][1311353e]: Awesome free and unlimited python library that implements Google Translate API

  [1311353e]: https://github.com/ssut/py-googletrans "Googletrans repo"
