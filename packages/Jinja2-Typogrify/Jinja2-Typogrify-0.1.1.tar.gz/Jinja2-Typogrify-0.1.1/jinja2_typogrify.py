#
# Jinja2-Typogrify
#
# Copyright (C) 2018 Boris Raicheff
# All rights reserved
#


from jinja2 import nodes
from jinja2.ext import Extension

from typogrify.filters import typogrify


class TypogrifyExtension(Extension):

    tags = {'typogrify'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(['name:endtypogrify'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_typogrify'), [], [], body).set_lineno(lineno)

    @staticmethod
    def _typogrify(caller):
        return typogrify(caller().unescape()).strip()


# EOF
