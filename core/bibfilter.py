################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013 by Philippe Faist                                       #
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

from butils import BibolamaziError

class BibFilterError(BibolamaziError):
    def __init__(self, filtername, errorstr):
        if (not isinstance(filtername, basestring)):
            filtername = '<unknown>'
        super(BibFilterError, self).__init__("filter `"+filtername+"': "+errorstr);




class BibFilter(object):

    # constants
    BIB_FILTER_SINGLE_ENTRY = 1;
    BIB_FILTER_BIBLIOGRAPHYDATA = 2;
    BIB_FILTER_BIBOLAMAZIFILE = 3;

    # subclasses should provide meaningful help texts
    helpauthor = "";
    helpdescription = "Some filter that filters some entries";
    helptext = "";

   
    def __init__(self, *pargs, **kwargs):
        self._bibolamazifile = None;
        super(BibFilter, self).__init__()

    def name(self):
        raise BibFilterError('<no name>', 'BibFilter subclasses must reimplement name()!')

    def action(self):
        raise BibFilterError(self.name(), 'BibFilter subclasses must reimplement action()!')

    def filter_bibentry(self, x):
        raise BibFilterError(self.name(), 'filter_bibentry() not implemented !')

    def filter_bibliographydata(self, x):
        raise BibFilterError(self.name(), 'filter_bibliographydata() not implemented !')

    def filter_bibolamazifile(self, x):
        raise BibFilterError(self.name(), 'filter_bibolamazifile() not implemented !')



    def setBibolamaziFile(self, bibolamazifile):
        """
        Remembers `bibolamazifile` as the `BibolamaziFile` object that we will be acting on.

        There's no use overriding this. When writing filters, there's also no need calling this
        explicitly, it's done in `BibolamaziFile`.
        """
        self._bibolamazifile = bibolamazifile;

    def bibolamaziFile(self):
        """
        Get the `BibolamaziFile` object that we are acting on. (The one previously set by
        `setBibolamaziFile()`.)

        There's no use overriding this.
        """
        return self._bibolamazifile;

    def cache_for(self, namespace, **kwargs):
        """
        Get access to the cache data stored within the namespace `namespace`. This directly
        queries the cache stored in the `BibolamaziFile` object set with
        `setBibolamaziFile()`.

        Returns a `BibUserCacheDic` object, or `None` if no bibolamazi file was set (which can
        only happen if you instantiate the filter explicitly yourself, which is usually not the
        case).

        When writing your filter, cache works transparently. Just call this function to access
        a specific cache.
        """
        if (self._bibolamazifile is not None):
            return self._bibolamazifile.cache_for(namespace, **kwargs)
        return None


    def getRunningMessage(self):
        """
        Return a nice message to display when invoking the fitler. The default implementation
        returns `self.name()`. Define this to whatever you want in your subclass.
        """
        return self.name();

    # convenience functions, no need to override
    @classmethod
    def getHelpAuthor(cls):
        """
        Convenience function that returns `helpauthor`, with whitespace stripped. Use this when
        getting the contents of the helpauthor text.

        There's no need to reimplement this function in your subclass.
        """
        return cls.helpauthor.strip();

    @classmethod
    def getHelpDescription(cls):
        """
        Convenience function that returns `helpdescription`, with whitespace stripped. Use this when
        getting the contents of the helpdescription text.

        There's no need to reimplement this function in your subclass.
        """
        return cls.helpdescription.strip();

    @classmethod
    def getHelpText(cls):
        """
        Convenience function that returns `helptext`, with whitespace stripped. Use this when
        getting the contents of the helptext text.

        There's no need to reimplement this function in your subclass.
        """
        return cls.helptext.strip();
    

# ------------------------------------------------------------------------


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
    thecls.type_arg_input = EnumArgType(thecls._values_list)
    # provide e.g. 'Mode.modes', 'Mode.modes_list', 'Mode.modes_dict' (or 'values_list' etc.)
    setattr(thecls, value_attr_name+'s', thecls._values)
    setattr(thecls, value_attr_name+'s_list', thecls._values_list)
    setattr(thecls, value_attr_name+'s_dict', thecls._values_dict)

    return thecls


# -------------------------------


class CommaStrListArgType:
    def __init__(self):
        pass

_rx_escape = re.compile(r'(\\|,)');
def _escape(x):
    return _rx_escape.sub(lambda m: '\\'+m.group(1), x);

_rx_unescape = re.compile(r'\\(?P<char>.)|\s*(?P<sep>,)\s*');

class CommaStrList(list):
    def __init__(self, iterable=[]):
        if (isinstance(iterable, basestring)):
            fullstr = iterable
            lastpos = 0
            strlist = []
            laststr = ""
            for m in _rx_unescape.finditer(iterable):
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
        return u",".join([_escape(unicode(x)) for x in self]);

    def __str__(self):
        return self.__unicode__().encode('utf-8')



