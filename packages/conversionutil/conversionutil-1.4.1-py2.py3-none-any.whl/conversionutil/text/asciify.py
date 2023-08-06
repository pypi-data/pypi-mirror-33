# encoding: utf-8

import logging_helper
from future.utils import iteritems

logging = logging_helper.setup_logging()


class ASCIIfy(object):

    UNICODE_LOOKUP = {u'A': u'AÀÁÂÄÆÃÅĀ',
                      u'C': u'CĆČ',
                      u'E': u'EÈÉÊËĒĖĘ',
                      u'I': u'IÌĮĪÍÏÎ',
                      u'L': u'LŁ',
                      u'N': u'NŃÑ',
                      u'O': u'OÕŌØŒÓÒÖÔ',
                      u'S': u'SŚŠ',
                      u'U': u'UŪÚÙÜÛ',
                      u'W': u'WŴ',
                      u'Y': u'YŶ',
                      u'Z': u'ZŽŹŻ',

                      u'a': u'aàáâäæãåā',
                      u'c': u'cçćč',
                      u'e': u'eèéêëēėę',
                      u'i': u'iìįīíïî',
                      u'l': u'lł',
                      u'n': u'nńñ',
                      u'o': u'oõōøœóòöô',
                      u's': u'sßśš',
                      u'u': u'uūúùüû',
                      u'w': u'wŵ',
                      u'y': u'yŷ',
                      u'z': u'zžźż',
                      }

    PUNCTUATION_CHARS = (u"""`¬!"£$%^&*()_+-=[]{};'#:@~\,./|<>?""")

    def __init__(self):
        self.UNICODE_REVERSE_LOOKUP = {}

        for key, values in iteritems(self.UNICODE_LOOKUP):
            for value in values:
                self.UNICODE_REVERSE_LOOKUP[value] = key

    def asciify(self,
                term):
        return u''.join([self.UNICODE_REVERSE_LOOKUP.get(c, c)
                         for c in term])

    def replace_punctuation_char(self,
                                 c):
        return (u' '
                if c in self.PUNCTUATION_CHARS
                else c)

    def replace_punctuation(self,
                            term):
        return u''.join([self.replace_punctuation_char(c)
                         for c in term]).replace(u'  ',
                                                 u' ')

    def strip_punctuation(self,
                            term):
        return u''.join([c for c in term
                         if c not in self.PUNCTUATION_CHARS]).replace(u'  ', u' ')


