from django.test import TestCase, Client
from django.urls import path
from json import loads
from googletrans import Translator
from .models import gTranslation
from .templatetags.gtranslate import gtranslate
from .urls import urlpatterns
from .urls_auth import urlpatterns as urlpatterns_auth
from .views import gTranslate, gTranslateAuth

# Create your tests here.

class TranslationStorage_TestCase(TestCase):
    """ requires makemigration and migrate before testing """
    src = 'en'
    dest = 'fr'
    text = 'something to translate'
    translation = "quelque chose à traduire"

    def test_translation_stored_and_returned(self):
        """ Translation stored and returned from the modal correctly """
        translation = gtranslate(self.text, self.dest, self.src, False)
        gTranslation.objects.create(
            text=self.text,
            language=self.dest,
            translation=translation
        )
        self.assertEquals(gTranslation.objects.get(
            text=self.text, language=self.dest
        ).translation, translation)

    def test_automatic_translation_storing(self):
        """ Test automatic translation storage """
        translation = gtranslate(
            self.text, self.dest, self.src, cache=True
        )
        self.assertEqual(
            gTranslation.objects.get(
                text=self.text, 
                language=self.dest).translation,
                translation
        )
        
    def test_translation_correctness(self):
        """ 
        Test if translation received from googleTrans is correct 
        on gtranslate.views.gTranslate no authorized
        """
        translation = gtranslate(
            self.text, self.dest, self.src, False
        )
        self.assertEqual(translation, self.translation)
    
    def test_dynamic_translation(self):
        """ Test dynamic translation url from urls.py.urlpatterns
        /<src>/<dest>/<text>
        """
        translation = loads(
            Client().get(
                "/gtran/%s/%s/%s" % (
                    self.src,
                    self.dest,
                    self.text
                )
            ).content
        )['translation']
        self.assertEqual(translation, self.translation)
        
    def test_dynamic_translation_auth(self):
        """ Test is_authorized dynamic translation url from 
        urls_auth.py.urlpatterns
        /<src>/<dest>/<text>
        """
        translation = Client().get(
                "/gtran_auth/%s/%s/%s" % (
                    self.src,
                    self.dest,
                    self.text
                )
            ).status_code
        self.assertEqual(translation, 302)

    def test_if_urls_loaded(self):
        """ test if urls of the view is on urls and urls_auth """
        self.assertEqual(
            path(
                '<src>/<dest>/<text>',
                gTranslate
            ).callback, urlpatterns[0].callback
        )
        self.assertEqual(
            path(
                '<src>/<dest>/<text>',
                gTranslateAuth
            ).callback, urlpatterns_auth[0].callback
        )

    def test_main_gtranslate_func(self):
        """ to test function which previous tests based on """
        T = Translator()
        translation = T.translate(self.text, self.dest, self.src).text
        self.assertEqual(translation, gtranslate(text=self.text, dest=self.dest, src=self.src))