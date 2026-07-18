#!/usr/bin/python3 -Bsu

## Copyright (C) 2014 troubadour <trobador@riseup.net>
## Copyright (C) 2014 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import locale, yaml

DEFAULT_LANG = 'en'

class _translations():
   def yaml_get(self):
      with open(self.path) as stream:
         data = yaml.safe_load(stream)
         self.xxx = data[self.section]
         ## Fall back to the DEFAULT_LANG translation MAPPING (not the literal
         ## string DEFAULT_LANG) when the current language is absent, so an
         ## unknown locale (e.g. a non-English LANG, or an unset C locale)
         ## resolves cleanly to English instead of tripping gettext's
         ## AttributeError-and-recover path, which prints a spurious ERROR line
         ## per translator on its first lookup.
         self.result = self.xxx.get(self.language, self.xxx.get(DEFAULT_LANG))

   def gettext(self, key):
      if self.result is None:
         self.yaml_get()
      try:
         text = self.result.get(key, None)
      except Exception:
         print('ERROR: No translation for language "{}", key "{}".'.format(self.language, key))
         self.language = DEFAULT_LANG
         self.yaml_get()
         text = self.result.get(key, None)
      return(text)

   def __init__(self, path, section):
      # credits to nrgaway.
      self.path = path
      self.section = section
      self.language = DEFAULT_LANG
      self.result = None
      try:
         if locale.getdefaultlocale()[0] != None:
            self.language = locale.getdefaultlocale()[0].split('_')[0]
      except Exception:
         self.language = DEFAULT_LANG
         print('ERROR: locale.getdefaultlocale failed. Using "{}" as default'.format(self.language))
      #print('self.language is {}'.format(self.language))
