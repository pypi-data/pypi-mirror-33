##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import six

from dataflake.fakeldap.utils import from_utf8


class Filter(object):
    """ A simple representation for search filter elements
    """

    def __init__(self, attr, comp, value):
        self.attr = attr
        self.comp = comp
        self.value = value.strip()

    def __repr__(self):
        repr_template = "Filter('%s', '%s', '%s')"
        if six.PY2:
            return repr_template % (self.attr, self.comp, self.value)
        else:
            return repr_template % (from_utf8(self.attr),
                                    from_utf8(self.comp),
                                    from_utf8(self.value))

    def __eq__(self, other):
        v1 = (self.attr.lower(), self.comp, self.value)
        v2 = (other.attr.lower(), other.comp, other.value)
        return v1 == v2

    def __lt__(self, other):
        v1 = (self.attr.lower(), self.comp, self.value)
        v2 = (other.attr.lower(), other.comp, other.value)
        return v1 < v2

    def __hash__(self):
        return id(self)

    def __call__(self, tree_pos, base):
        res = []
        query_value = self.value[:]
        wildcard = False

        if six.PY2 and isinstance(base, six.text_type):
            base = base.encode('UTF-8')

        if query_value.startswith(b'*') or query_value.endswith(b'*'):
            if query_value != b'*':
                # Wildcard search
                if query_value.startswith(b'*') and query_value.endswith(b'*'):
                    wildcard = 'both'
                    query_value = query_value[1:-1]
                elif query_value.startswith(b'*'):
                    wildcard = 'start'
                    query_value = query_value[1:]
                elif query_value.endswith(b'*'):
                    wildcard = 'end'
                    query_value = query_value[:-1]

        for rdn, record in tree_pos.items():
            found = True

            if self.attr in record:
                if query_value == b'*':
                    # Always include if there's a value for it.
                    pass
                elif wildcard:
                    found = False
                    for x in record[self.attr]:
                        if wildcard == 'start':
                            if x.endswith(query_value):
                                found = True
                                break
                        elif wildcard == 'end':
                            if x.startswith(query_value):
                                found = True
                                break
                        else:
                            if query_value in x:
                                found = True
                                break
                elif query_value not in record[self.attr]:
                    found = False

                if found:
                    if base.startswith(rdn):
                        dn = base
                    else:
                        dn = b'%s,%s' % (rdn, base)
                    res.append((dn, record))

        return res
