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

from ..butils import BibolamaziError


class BibFilterError(BibolamaziError):
    def __init__(self, filtername, errorstr):
        if (not isinstance(filtername, basestring)):
            filtername = '<unknown>'
        super(BibFilterError, self).__init__("filter `"+filtername+"': "+errorstr);



class BibFilter(object):
    """
    Base class for a `bibolamazi` filter.

    """

    # constants
    BIB_FILTER_SINGLE_ENTRY = 1;
    BIB_FILTER_BIBOLAMAZIFILE = 3;

    # subclasses should provide meaningful help texts
    helpauthor = "";
    helpdescription = "Some filter that filters some entries";
    helptext = "";

   
    def __init__(self, *pargs, **kwargs):
        self._bibolamazifile = None;
        super(BibFilter, self).__init__()
        self._filtername = self.__class__.__name__

    def name(self):
        """
        Returns the name of the filter as it was invoked in the bibolamazifile. This might
        be with, or without, the filterpackage. This information should
        be only used for reporting purposes and might slightly vary.

        If the filter was instantiated manually, and `set_invokation_name()` was not
        called, then this function returns the class name.

        The subclass should not reimplement this function unless it really really really
        *really* feels it needs to.
        """
        return self._filtername

    def set_invokation_name(self, filtername):
        """
        Called internally by bibolamazifile, so that `name()` returns the name by which
        this filter was invoked.

        This function sets exactly what `name()` will return. Subclasses should not
        reimplement, the default implementation should suffice.
        """
        self._filtername = filtername

    def action(self):
        """
        Return one of `BibFilter.BIB_FILTER_SINGLE_ENTRY` or
        `BibFilter.BIB_FILTER_BIBOLAMAZIFILE`, which tells how this filter should
        function. Depending on the return value of this function, either
        `filter_bibentry()` or `filter_bibolamazifile()` will be called.

        Note that when the filter is instantiated within `BibolamaziFile`, then the
        function `bibolamaziFile()` will always return a valid object, independently of
        the filter's way of acting.
        """
        raise BibFilterError(self.name(), 'BibFilter subclasses must reimplement action()!')

    def filter_bibentry(self, x):
        """
        The main filter function for filters that filter the data entry by entry.
        
        If the subclass' `action()` function returns `BibFilter.BIB_FILTER_SINGLE_ENTRY`,
        then the subclass must reimplement this function. Otherwise, this function is
        never called.

        The object `x` is a `pybtex.database.Entry` object instance, which should be
        updated according to the filter's action and purpose.

        The return value of this function is ignored. Subclasses should report warnings
        and logging through `core.blogger.logger` and should raise errors as
        `BibFilterError` (preferrably, a subclass). Other raised exceptions will be
        interpreted as internal errors and will open a debugger.
        """
        raise BibFilterError(self.name(), 'filter_bibentry() not implemented !')

    def filter_bibolamazifile(self, x):
        """
        The main filter function for filters that filter the data entry by entry.
        
        If the subclass' `action()` function returns `BibFilter.BIB_FILTER_SINGLE_ENTRY`,
        then the subclass must reimplement this function. Otherwise, this function is
        never called.

        The object `x` is a `core.bibolamazifile.BibolamaziFile` object instance, which
        should be updated according to the filter's action and purpose.

        The return value of this function is ignored. Subclasses should report warnings
        and logging through `core.blogger.logger` and should raise errors as
        `BibFilterError` (preferrably, a subclass). Other raised exceptions will be
        interpreted as internal errors and will open a debugger.
        """
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
        Return a nice message to display when invoking the fitler. The default
        implementation returns `self.name()`. Define this to whatever you want in your
        subclass to describe what you're doing. The core bibolamazi program displays this
        information to the user as it runs the filter.
        """
        return self.name();


    # convenience functions, no need to (i.e. should not) override
    @classmethod
    def getHelpAuthor(cls):
        """
        Convenience function that returns `helpauthor`, with whitespace stripped. Use this
        when getting the contents of the helpauthor text.

        There's no need to (translate: you should not) reimplement this function in your subclass.
        """
        return cls.helpauthor.strip();

    @classmethod
    def getHelpDescription(cls):
        """
        Convenience function that returns `helpdescription`, with whitespace stripped. Use
        this when getting the contents of the helpdescription text.

        There's no need to (translate: you should not) reimplement this function in your subclass.
        """
        return cls.helpdescription.strip();

    @classmethod
    def getHelpText(cls):
        """
        Convenience function that returns `helptext`, with whitespace stripped. Use this
        when getting the contents of the helptext text.

        There's no need to (translate: you should not) reimplement this function in your subclass.
        """
        return cls.helptext.strip();
    


