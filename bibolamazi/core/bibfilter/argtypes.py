################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2014 by Philippe Faist                                       #
#   philippe.faist@bluewin.ch                                                  #
#                                                                              #
#   Bibolamazi is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   Bibolamazi is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with Bibolamazi.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                              #
################################################################################

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr


import re

import bibolamazi.init
from .. import butils



# for meta-typing. This is particularly used by the graphical interface.
class EnumArgType:
    def __init__(self, listofvalues):
        self.listofvalues = listofvalues

    # magic method that produces a representation of the option value for the
    # command-line string. Must return a bool (for -d...) or a string (for
    # -s...).
    def option_val_repr(self, x):
        return str(x)


def enum_class(class_name, values, default_value=0, value_attr_name='value'):
    """
    `class_name` is the class name.
    
    `values` should be a list of tuples `(string_key, numeric_value)` of all the
    expected string names and of their corresponding numeric values.
    
    `default_value` should be the value that would be taken by default, e.g. by
    using the default constructor.
    
    `value_attr_name` the name of the attribute in the class that should store the
    value. For example, the `arxiv` module defines the enum class `Mode` this way
    with the attribute `mode`, so that the numerical mode can be obtained with
    `enumobject.mode`.
    """

    @python_2_unicode_compatible
    class ThisEnumArgClass:
        _values = values
        _values_list = [x[0] for x in _values]
        _values_dict = dict(_values)

        def __init__(self, val=None):
            # this will call _parse_value(), and also assign the default_value if
            # val is None.
            self._value = val

        def __setattr__(self, attname, val):
            if (attname == value_attr_name or attname == '_value'):
                theval = self._parse_value(val)
                self.__dict__[value_attr_name] = theval
                self.__dict__['_value'] = theval
                return
            self.__dict__[attname] = val

        def _parse_value(self, value):
            # easy cases.
            if (isinstance(value, int)):
                return value
            if (isinstance(value, self.__class__)):
                return value._value

            # request for default value
            if (value is None):
                # just make sure default_value is not None, to avoid infinite recursion.
                return (0 if default_value is None else self._parse_value(default_value))

            # value given by key
            svalue = unicodestr(value)
            if (svalue in self._values_dict):
                return self._values_dict.get(svalue)
            try:
                return int(value)
            except ValueError:
                pass

            raise ValueError("%s: Invalid value: %r" %(self.__class__.__name__, value))

        # so that we can use this object like an int, at least compare it to an int or to the
        # string corresponding to the other mode
        def __eq__(self, other):
            if (isinstance(other, int)):
                return self._value == other
            if (isinstance(other, self.__class__)):
                return self._value == other._value
            return self._value == self._parse_value(other)

        def __str__(self):
            ok = [x for (x,v) in self._values if v == self._value]
            if (not len(ok)):
                # this doesn't correspond to a valid value... return the integer value directly
                return str(self._value)
            # the corresponding string key for this value
            return ok[0]

        def __repr__(self):
            return "%s('%s')"%(self.__class__.__name__, self.__str__())

        def __hash__(self):
            return hash(self.value)

    thecls = ThisEnumArgClass
    thecls.__name__ = str(class_name)
    # add docstring
    mapped_vals_list = [ "`%s`"%(x) for x in thecls._values_list ]
    if len(mapped_vals_list) > 1:
        show_vals_list = ", ".join(mapped_vals_list[:-1]) + ", or "+mapped_vals_list[-1]
    elif len(mapped_vals_list) == 1:
        show_vals_list = mapped_vals_list[0]
    else:
        show_vals_list = '<no values>'
    thecls.__doc__ = "An enumeration type which may have one of the following values: %s."%(
        show_vals_list
        )
    # for the gui
    thecls.type_arg_input = EnumArgType(thecls._values_list)
    # provide e.g. 'Mode.modes', 'Mode.modes_list', 'Mode.modes_dict' (or 'values_list' etc.)
    setattr(thecls, value_attr_name+'s', thecls._values)
    setattr(thecls, value_attr_name+'s_list', thecls._values_list)
    setattr(thecls, value_attr_name+'s_dict', thecls._values_dict)

    return thecls






# ------------------------------------------------------------------------------




# for meta-typing. This is particularly used by the graphical interface.
class MultiTypeArgType:
    def __init__(self, typelist, parse_value_fn):
        self.typelist = typelist
        self.parse_value_fn = parse_value_fn

    # magic method that produces a representation of the option value for the
    # command-line string. Must return a bool (for -d...) or a string (for
    # -s...).
    def option_val_repr(self, x):
        if isinstance(x.value, bool):
            return bool(x.value)
        return str(x.value)


multi_type_class_default_convert_functions = [
    (bool, butils.getbool),
]

def multi_type_class(class_name, typelist,
                     value_attr_name='value', valuetype_attr_name='valuetype',
                     convert_functions=multi_type_class_default_convert_functions,
                     parse_value_fn=None, doc=None):
    """
    `class_name` is the class name.
    
    `typelist` should be a list of tuples `(typeobject, description)` of type
    objects that can be stored by this object and a corresponding very short
    description of what is stored with that type
    
    `default_value` should be the value that would be taken by default, e.g. by
    using the default constructor.
    
    `value_attr_name` the name of the attribute in the class that should store the
    value.

    `valuetype_attr_name` the name of the attribute in the class that should store the
    type object that is currently stored.

    Optionally, you can also specify a list of helper functions that can convert
    stuff into a given type: `convert_functions` is a list of tuples
    `(type_object, function)` that specifies this.

    If `parse_value_fn` is not None, then it should be set to a callable that
    parses a value and returns a tuple `(typeobject, value)`. It can raise
    `ValueError`.
    """


    def parse_value_impl(value,
                         typelist=typelist,
                         convert_functions=convert_functions,
                         parse_value_fn=parse_value_fn):
        if parse_value_fn is not None:
            return parse_value_fn(value)

        if value is None:
            t = typelist[0][0]
            return (t, t()) # instantiate first type

        # try to convert in order of types
        for t,s in typelist:

            cfn = t
            cfnlst = [cfn2 for t2,cfn2 in convert_functions if t is t2]
            if len(cfnlst):
                cfn = cfnlst[0]

            try:
                # try to convert to this type
                theval = cfn(value)
                return t, theval # return if successful
            except (TypeError,ValueError):
                continue

        # none of that worked
        raise ValueError("Invalid value: %r" %(value,))


    @python_2_unicode_compatible
    class ThisMultiTypeArgClass:
        _typelist = typelist

        def __init__(self, *args):
            # X() or X(value) or X(type, value)
            
            if len(args) == 0: # X()
                t, v = self.parse_value(None)
                
            elif len(args) == 1: # X(x) or X(value)
                if isinstance(args[0], self.__class__):
                    t, v = args[0]._valuetype, args[0]._value
                else:
                    t, v = self.parse_value(args[0])

            elif len(args) == 2: # X(type, value)
                t, v = args

            else:
                raise TypeError("Wrong number of arguments: %d"%(len(args)))

            self.set_type_value(t, v)

        def __setattr__(self, attname, val):
            if (attname == value_attr_name):
                thetyp, theval = self.parse_value(val)
                self.set_type_value(thetyp, theval)
                return
            self.__dict__[attname] = val

        def set_type_value(self, thetyp, theval):
            #print("set_type_value(%r,%r)"%(thetyp,theval))
            if len([t for t,s in self._typelist if t is thetyp]) != 1:
                raise ValueError("Invalid type: %r"%(thetyp,))

            # ### Don't be this strict -- for instance, we should accept int for bool ...
            #if not isinstance(theval, thetyp):
            #    raise ValueError("Value is not of given type: %r (expected type %s)"
            #                     %(theval, thetyp.__name__))

            self.__dict__[valuetype_attr_name] = thetyp
            self.__dict__[value_attr_name] = theval
            self.__dict__['_valuetype'] = thetyp
            self.__dict__['_value'] = theval

        @staticmethod
        def parse_value(value):
            return parse_value_impl(value)

        # so that we can use this object like an int, at least compare it to an int or to the
        # string corresponding to the other mode
        def __eq__(self, other):
            if (isinstance(other, self.__class__)):
                return self._valuetype is other._valuetype and self._value == other._value
            return self == self.__class__(other)

        def __str__(self):
            return str(self._value)

        def __repr__(self):
            return "%s(%r)"%(self.__class__.__name__, self._value)

        def __hash__(self):
            return hash(self._value)

    thecls = ThisMultiTypeArgClass
    thecls.__name__ = str(class_name)
    # add docstring
    if doc is None:
        mapped_vals_list = [ "`%s` (%s)"%(t.__name__, s) for t,s in thecls._typelist ]
        if len(mapped_vals_list) > 1:
            show_vals_list = ", ".join(mapped_vals_list[:-1]) + ", or "+mapped_vals_list[-1]
        elif len(mapped_vals_list) == 1:
            show_vals_list = mapped_vals_list[0]
        else:
            show_vals_list = '<no types>'
        doc = "A class which can store a value of one of the following types: %s."%(
            show_vals_list,
            )
        for t, s in thecls._typelist:
            if hasattr(t, '__doc__'):
                doc += "\n\n" + str(t.__name__) + ": " + t.__doc__
    thecls.__doc__ = doc
    # for the gui
    thecls.type_arg_input = MultiTypeArgType(thecls._typelist, parse_value_impl)

    return thecls



# ------------------------------------------------------------------------------



class StrEditableArgType(object):
    def __init__(self):
        pass

    # magic method that produces a representation of the option value for the
    # command-line string. Must return a bool (for -d...) or a string (for
    # -s...).
    def option_val_repr(self, x):
        return str(x)



# ------------------------------------------------------------------------------




#_rx_escape_lst = re.compile(r'(\\|,)')
#def _escape_lst(x):
#    return _rx_escape_lst.sub(lambda m: '\\'+m.group(1), x)

#_rx_unescape_lst = re.compile(r'\\(?P<char>.)|\s*(?P<sep>,)\s*')

@python_2_unicode_compatible
class CommaStrList(list):
    """
    A list of values, specified as a comma-separated string.
    """
    def __init__(self, iterable=[]):
        # if (isinstance(iterable, basestring)):
        #     fullstr = iterable
        #     lastpos = 0
        #     strlist = []
        #     laststr = ""
        #     for m in _rx_unescape_lst.finditer(iterable):
        #         laststr += fullstr[lastpos:m.start()]
        #         if (m.group('sep') == ','):
        #             strlist.append(laststr)
        #             laststr = ""
        #         # ### DON'T ALLOW ESCAPES, THIS MESSES BADLY WITH LATEX STUFF
        #         #elif (m.group() and m.group()[0] == '\\'):
        #         #    # escaped char
        #         #    laststr += m.group('char')
        #         else:
        #             raise RuntimeError("Unexpected match!?: %r", m)
        #         lastpos = m.end()
        #     # include the last bit of string
        #     laststr += fullstr[lastpos:]
        #     strlist.append(laststr)

        #     # now we've got our decoded string list.
        #     iterable = strlist
        if isinstance(iterable, basestring):
            iterable = iterable.split(',')
            
        super(CommaStrList, self).__init__(iterable)

    type_arg_input = StrEditableArgType()

    def __str__(self):
        return u",".join([unicodestr(x) for x in self])



# ------------------------------------------------------------------------------


# _rx_escape_dic = re.compile(r'(\\|,|:)')
# def _escape_dic(x):
#     return _rx_escape_dic.sub(lambda m: '\\'+m.group(1), x)
#
# _rx_unescape_val = re.compile(r'\\(?P<char>.)')
# _rx_unescape_keyvalsep = re.compile(r'\s*(?P<sep>:)\s*')
_rx_keyvalsep = re.compile(r'\s*(?P<sep>:)\s*')

@python_2_unicode_compatible
class ColonCommaStrDict(dict):
    """
    A dictionary of values, specified as a comma-separated string of pairs
    ``'key:value'``. If no value is given (no colon), then the value is `None`.
    """
    def __init__(self, *args, **kwargs):

        if len(args) == 1:
            iterable = args[0]
        elif len(args) == 0:
            iterable = None
        else:
            raise ValueError('ColonCommaStrDict accepts at most one *arg, an iterable')
        
        if isinstance(iterable, basestring):
            pairlist = CommaStrList(iterable)
            d = {}
            # now, read each key/value pair
            for pairstr in pairlist:
                #m = _rx_unescape_keyvalsep.search(pairstr)
                m = _rx_keyvalsep.search(pairstr)
                if m:
                    key = pairstr[:m.start()]
                    val = pairstr[m.end():]
                else:
                    key = pairstr
                    val = None
                # key = _rx_unescape_val.sub(lambda m: m.group('char'), key)
                # if val:
                #    val = _rx_unescape_val.sub(lambda m: m.group('char'), val)

                if key in d:
                    raise ValueError("Repeated key in input: %s"%(key,))

                d[key] = val

            super(ColonCommaStrDict, self).__init__(d)

        else:

            super(ColonCommaStrDict, self).__init__(*args, **kwargs)

    type_arg_input = StrEditableArgType()

    def __str__(self):
        return u",".join([unicodestr(k)+(':'+unicodestr(v) if v is not None else '')
                          for k,v in iteritems(self)])




#
# A special type for a Logging Level
#

import logging
from bibolamazi.core.blogger import LONGDEBUG

LogLevel = enum_class('LogLevel',
                      [('CRITICAL', logging.CRITICAL),
                       ('ERROR', logging.ERROR),
                       ('WARNING', logging.WARNING),
                       ('INFO', logging.INFO),
                       ('DEBUG', logging.DEBUG),
                       ('LONGDEBUG', LONGDEBUG)],
                      default_value='INFO',
                      value_attr_name='levelno')
