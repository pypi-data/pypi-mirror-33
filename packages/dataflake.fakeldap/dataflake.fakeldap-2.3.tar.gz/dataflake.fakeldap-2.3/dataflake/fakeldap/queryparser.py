# -*- coding: utf-8 -*-
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

import re

import six

from dataflake.fakeldap.op import Op
from dataflake.fakeldap.queryfilter import Filter
from dataflake.fakeldap.utils import utf8_string

# From http://www.ietf.org/rfc/rfc2254.txt, Section 4
# with references to http://www.ietf.org/rfc/rfc2251.txt
#
# filter     = "(" filtercomp ")"
# filtercomp = and / or / not / item
# and        = "&" filterlist
# or         = "|" filterlist
# not        = "!" filter
# filterlist = 1*filter
# item       = simple / present / substring / extensible
# simple     = attr filtertype value
# filtertype = equal / approx / greater / less
# equal      = "="
# approx     = "~="
# greater    = ">="
# less       = "<="
# extensible = attr [":dn"] [":" matchingrule] ":=" value
#              / [":dn"] ":" matchingrule ":=" value
# present    = attr "=*"
# substring  = attr "=" [initial] any [final]
# initial    = value
# any        = "*" *(value "*")
# final      = value
# attr       = AttributeDescription from Section 4.1.5 of RFC 2251
# matchingrule = MatchingRuleId from Section 4.1.9 of RFC 2251
# value      = AttributeValue from Section 4.1.6 of RFC 2251


_FLTR = br'\(\w*?=[\*\w\s=,\\]*?\)'
_OP = b'[&\|\!]{1}'

FLTR = (br'\((?P<attr>\w*?)(?P<comp>=)' +
        br'(?P<value>[\*\w\s=,\\\'@\-\+_\.^\W\d_]*?)\)' +
        b'(?P<fltr>.*)')
FLTR_RE = re.compile(FLTR.decode(), re.UNICODE)

FULL = b'\((?P<op>(%s))(?P<fltr>.*)\)' % _OP
FULL_RE = re.compile(FULL)

OP = b'\((?P<op>(%s))(?P<fltr>(%s)*)\)' % (_OP, _FLTR)
OP_RE = re.compile(OP)


class Parser(object):

    @utf8_string('query')
    def parse_query(self, query, recurse=False):
        """ Parse a query string into a series of Ops and Filters
        """
        parts = []
        for expr in (OP_RE, FULL_RE):
            # Match outermost operations
            m = expr.match(query)
            if m:
                d = m.groupdict()
                op = Op(d['op'])
                sub = self.parse_query(d['fltr'])
                if recurse:
                    parts.append((op, sub))
                else:
                    parts.append(op)
                    parts.append(sub)
                rest = query[m.end():]
                if rest:
                    parts.extend(self.parse_query(rest))
                return tuple(parts)

        # Under Python 3, our regular expression is type <str>, which
        # does not handle <bytes>. Doing a temporary decode.
        decode_needed = six.PY3 and isinstance(query, bytes)
        if decode_needed:
            query = query.decode('UTF-8')

        # Match internal filter.
        d = FLTR_RE.match(query).groupdict()

        # Revert the previous temporary decode
        if decode_needed:
            for k, v in d.items():
                d[k] = v.encode('UTF-8')

        parts.append(Filter(d['attr'], d['comp'], d['value']))
        if d['fltr']:
            parts.extend(self.parse_query(d['fltr'], recurse=True))
        return tuple(parts)

    def flatten_query(self, query, klass=Filter):
        """ Flatten a sequence of Ops/Filters leaving only ``klass`` instances
        """
        q = [f for f in query if isinstance(f, klass)]
        for item in query:
            if isinstance(item, tuple):
                q.extend(self.flatten_query(item, klass))
        return tuple(q)

    def explode_query(self, query):
        """ Separate a parsed query into operations
        """
        res = []

        def dig(sub, res):
            level = []
            for item in sub:
                if isinstance(item, tuple):
                    got = dig(item, res)
                    if got and level and isinstance(level[0], Op):
                        level.append(got)
                        res.append(tuple(level))
                        level = []
                else:
                    level.append(item)
            return tuple(level)

        level = dig(query, res)
        if not res:
            # A simple filter with no operands
            return ((Op(b'&'), level),)
        if level:
            # Very likely a single operand around a group of filters.
            assert len(level) == 1, (len(level), level)
            res.append((level[0], ()))
        return tuple(res)

    def cmp_query(self, query, other, strict=False):
        """ Compare parsed queries and return common query elements
        """
        q1 = self.flatten_query(query)
        q2 = self.flatten_query(other)

        if strict:
            return q1 == q2

        for fltr in q2:
            if fltr in q1:
                return fltr
