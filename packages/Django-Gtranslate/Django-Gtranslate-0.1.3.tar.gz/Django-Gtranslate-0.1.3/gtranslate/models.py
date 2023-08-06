from django.db import models

class gTranslation(models.Model):
    text = models.TextField(max_length=2100)
    language = models.TextField(max_length=50)
    translation = models.TextField(max_length=4000)
