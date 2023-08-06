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

from base64 import b64encode
import functools
from hashlib import sha1 as sha_new
import inspect
import ldap.dn
import six


def hash_pwd(pwd_str):
    if isinstance(pwd_str, six.text_type):
        pwd_str = pwd_str.encode('utf-8')
    sha_digest = sha_new(pwd_str).digest()
    return b'{SHA}%s' % b64encode(sha_digest).strip()


def explode_dn(dn):
    if isinstance(dn, six.text_type):
        # DNs are expected to be UTF-8-encoded
        dn = dn.encode('UTF-8')

    parts = []
    raw_parts = ldap.dn.explode_dn(dn)
    for part in raw_parts:
        if isinstance(part, six.text_type):
            part = part.encode('UTF-8')
        parts.append(part)

    return parts


def to_utf8(to_convert):
    if not isinstance(to_convert, six.binary_type):
        to_convert = to_convert.encode('UTF-8')
    return to_convert


def from_utf8(to_convert):
    if isinstance(to_convert, six.binary_type):
        to_convert = to_convert.decode('UTF-8')
    return to_convert


def utf8_string(*tested):
    """ Decorator function to check one or more function arguments
    """

    def _check_utf8_string(called_function):
        if six.PY2:
            spec = inspect.getargspec(called_function)
        else:
            spec = inspect.getfullargspec(called_function)
        test_indices = [(x, spec[0].index(x)) for x in tested if x in spec[0]]

        @functools.wraps(called_function)
        def _check(*args, **kw):
            for arg_name, arg_index in test_indices:
                if arg_name in kw:
                    arg_val = kw.get(arg_name)
                elif arg_index < len(args):
                    arg_val = args[arg_index]
                else:
                    continue  # fallback to default arguments

                if not isinstance(arg_val, six.binary_type):
                    msg = 'Parameter %s must be UTF-8, found %s (%s)'
                    raise TypeError(msg % (arg_name,
                                           str(arg_val),
                                           type(arg_val)))

            return called_function(*args, **kw)

        return _check

    return _check_utf8_string
