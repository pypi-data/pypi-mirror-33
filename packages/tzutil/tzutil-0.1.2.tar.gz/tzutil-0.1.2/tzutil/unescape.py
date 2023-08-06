# -*- coding: utf-8 -*-

import html.entities
import re
from urllib.parse import urlparse

BLOD_LINE = re.compile(r"^\s*\*\*[\r\n]+", re.M)

_char = re.compile(r'&(\w+?);')
_dec = re.compile(r'&#(\d{2,4});')
_hex = re.compile(r'&#x(\d{2,4});')


def _char_unescape(m, defs=html.entities.entitydefs):
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0)


import re
import html.entities


def unescape(s):
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in html.entities.name2codepoint:
            return chr(html.entities.name2codepoint[entity])
        return " "  # Unknown entity: We replace with a space.
    t = re.sub(
        '&(%s);' % '|'.join(html.entities.name2codepoint), entity2char, s)

    # Then convert numerical entities (such as &#233;)
    t = re.sub('&#(\d+);', lambda x: chr(int(x.group(1))), t)

    # Then convert hexa entities (such as &#x00E9;)
    return re.sub('&#x(\w+);', lambda x: chr(int(x.group(1), 16)), t)


if __name__ == '__main__':
    print((unescape("""<option value='&#20013;&#22269;&#35821;&#35328;&#25991;&#23398;&#31995;'>&#20013;&#22269;&#35821;&#35328;&#25991;&#23398;&#31995;</option>""")))
