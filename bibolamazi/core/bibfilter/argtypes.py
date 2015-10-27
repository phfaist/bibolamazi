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

import re

import bibolamazi.init




# for meta-typing. This is particularly used by the graphical interface.


class EnumArgType:
    def __init__(self, listofvalues):
        self.listofvalues = listofvalues


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

    class ThisEnumArgClass:
        _values = values;
        _values_list = [x[0] for x in _values]
        _values_dict = dict(_values)

        def __init__(self, val=None):
            # this will call _parse_value(), and also assign the default_value if
            # val is None.
            self._value = val

        def __setattr__(self, attname, val):
            if (attname == value_attr_name or attname == '_value'):
                theval = self._parse_value(val)
                self.__dict__[value_attr_name] = theval;
                self.__dict__['_value'] = theval;
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
            svalue = str(value)
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
    thecls.__name__ = class_name
    # add docstring
    mapped_vals_list = [ "`%s'"%(x) for x in thecls._values_list ]
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






class CommaStrListArgType:
    def __init__(self):
        pass

_rx_escape_lst = re.compile(r'(\\|,)');
def _escape_lst(x):
    return _rx_escape_lst.sub(lambda m: '\\'+m.group(1), x);

_rx_unescape_lst = re.compile(r'\\(?P<char>.)|\s*(?P<sep>,)\s*');

class CommaStrList(list):
    """
    A list of values, specified as a comma-separated string.
    """
    def __init__(self, iterable=[]):
        if (isinstance(iterable, basestring)):
            fullstr = iterable
            lastpos = 0
            strlist = []
            laststr = ""
            for m in _rx_unescape_lst.finditer(iterable):
                laststr += fullstr[lastpos:m.start()];
                if (m.group('sep') == ','):
                    strlist.append(laststr)
                    laststr = ""
                elif (m.group() and m.group()[0] == '\\'):
                    # escaped char
                    laststr += m.group('char');
                else:
                    raise RuntimeError("Unexpected match!?: %r", m)
                lastpos = m.end()
            # include the last bit of string
            laststr += fullstr[lastpos:];
            strlist.append(laststr);

            # now we've got our decoded string list.
            iterable = strlist
            
        super(CommaStrList, self).__init__(iterable)

    def __unicode__(self):
        return u",".join([_escape_lst(unicode(x)) for x in self]);

    def __str__(self):
        return self.__unicode__().encode('utf-8')



# ------------------------------------------------------------------------------


class ColonCommaStrDictArgType:
    def __init__(self):
        pass

_rx_escape_dic = re.compile(r'(\\|,:)');
def _escape_dic(x):
    return _rx_escape_dic.sub(lambda m: '\\'+m.group(1), x);

_rx_unescape_val = re.compile(r'\\(?P<char>.)');
_rx_unescape_keyvalsep = re.compile(r'\s*(?P<sep>:)\s*');

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
        
        if (isinstance(iterable, basestring)):
            pairlist = CommaStrList(iterable)
            d = {}
            # now, read each key/value pair
            for pairstr in pairlist:
                m = _rx_unescape_keyvalsep.search(pairstr)
                if m:
                    key = pairstr[:m.start()]
                    val = pairstr[m.end():]
                else:
                    key = pairstr
                    val = None
                key = _rx_unescape_val.sub(lambda m: m.group('char'), key)
                if val:
                    val = _rx_unescape_val.sub(lambda m: m.group('char'), val)

                if key in d:
                    raise ValueError("Repeated key in input: %s"%(key))

                d[key] = val

            super(ColonCommaStrDict, self).__init__(d)

        else:

            super(ColonCommaStrDict, self).__init__(*args, **kwargs)


    def __unicode__(self):
        return u",".join([_escape_dic(unicode(k))+(':'+_escape_dic(unicode(v)) if v is not None else '')
                          for k,v in self.iteritems()]);

    def __str__(self):
        return self.__unicode__().encode('utf-8')



