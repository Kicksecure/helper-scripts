#!/usr/bin/python3 -u

## Copyright (C) 2014 troubadour <trobador@riseup.net>
## Copyright (C) 2014 - 2020 ENCRYPTED SUPPORT LP <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import sys
import locale, yaml

DEFAULT_LANG = 'en'

class _translations():
   def yaml_get(self):
      with open(self.path) as stream:
         data = yaml.safe_load(stream)
         self.xxx = data[self.section]
         self.result = self.xxx.get(self.language, DEFAULT_LANG)

   def gettext(self, key):
      if self.result == None:
         self.yaml_get()
      try:
         text = self.result.get(key, None)
      except:
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
      except:
         self.language = DEFAULT_LANG
         print('ERROR: locale.getdefaultlocale failed. Using "{}" as default'.format(self.language))
      #print('self.language is {}'.format(self.language))
