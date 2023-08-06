
from modeltranslation.translator import translator

from flatpages.models import FlatPage


translator.register(FlatPage, fields=['title', 'content'])
