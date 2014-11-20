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
    """
    Exception a filter should raise if it encounters an error.
    """
    def __init__(self, filtername, message):
        if (not isinstance(filtername, basestring)):
            filtername = '<unknown>'
        super(BibFilterError, self).__init__(u"Filter `"+filtername+"': "+unicode(message));
        self.filtername = filtername
        self.message = message




class BibFilter(object):
    """
    Base class for a `bibolamazi` filter.

    To write new filters, you should subclass `BibFilter` and reimplement the relevant
    methods. See documentation of the different methods below to understand which to
    reimplement.
    """

    # constants
    BIB_FILTER_SINGLE_ENTRY = 1;
    """
    A constant that indicates that the filter should act upon individual entries only. 
    See documentation for the :py:meth:`action()` method for more details.
    """

    BIB_FILTER_BIBOLAMAZIFILE = 3;
    """
    A constant that indicates that the filter should act upon the whole bibliography at
    once. See documentation for the :py:meth:`action()` method for more details.
    """

    # subclasses should provide meaningful help texts
    helpauthor = "";
    """
    Your subclass should provide a `helpauthor` attribute, containing a one-line notice
    with the name of the author that wrote the filter code. You may also add a copyright
    notice. The exact format is not specified. This text is typically displayed at the top
    of the page generated by ``bibolamazi --help <filter>``.

    You should also avoid accessing this class attribute, you should use
    :py:meth:`getHelpAuthor()` instead, which will ensure that whitespace is properly
    stripped.
    """

    helpdescription = "Some filter that filters some entries";
    """
    Your subclass should provide a `helpdescription` attribute, containing a one-line
    description of what your filter does. This is typically displayed when invoking
    ``bibolamazi --list-filters``, along with the filter name.

    You should also avoid accessing this class attribute, you should use
    :py:meth:`getHelpDescription()` instead, which will ensure that whitespace is properly
    stripped.
    """

    helptext = "";
    """
    Your subclass should provide a `helptext` attribute, containing a possibly long, as
    detailed as possible description of how to use your filter. You don't need to provide
    the basic 'usage' and option list, which are automatically generated; but you should
    include all the text that would appear after the option list. This is typically
    displayed when invoking ``bibolamazi --help <filter>``.

    You should also avoid accessing this class attribute, you should use
    :py:meth:`getHelpText()` instead, which will ensure that whitespace is properly
    stripped.
    """

   
    def __init__(self, *pargs, **kwargs):
        """
        Constructor. No particular arguments are expected; any received are passed further
        to superclasses.
        """
        self._bibolamazifile = None;
        super(BibFilter, self).__init__(*pargs, **kwargs)
        self._filtername = self.__class__.__name__


    def action(self):
        """
        Return one of :py:const:`~BibFilter.BIB_FILTER_SINGLE_ENTRY` or
        :py:const:`~BibFilter.BIB_FILTER_BIBOLAMAZIFILE`, which tells how this filter
        should function. Depending on the return value of this function, either
        :py:meth:`filter_bibentry()` or :py:meth:`filter_bibolamazifile()` will be called.

        If the filter wishes to act on individual entries (like the built-in `arxiv` or
        `url` filters), then the subclass should return
        :py:const:`BibFilter.BIB_FILTER_SINGLE_ENTRY`. At the time of filtering the data,
        the function :py:meth:`filter_bibentry()` will be called repeatedly for each entry
        of the database.

        If the filter wishes to act on the full database at once (like the built-in
        `duplicates` filter), then the subclass should return
        :py:const:`~BibFilter.BIB_FILTER_BIBOLAMAZIFILE`. At the time of filtering the
        data, the function :py:meth:`filter_bibolamazifile()` will be called once with the
        full :py:class:`~core.bibolamazifile.BibolamaziFile` object as parameter. Note
        this is the only way to add or remove entries to or from the database, or to
        change their order.

        Note that when the filter is instantiated by a
        :py:class:`~core.bibolamazifile.BibolamaziFile` (as is most of the time in
        practice), then the function :py:meth:`bibolamaziFile()` will always return a
        valid object, independently of the filter's way of acting.
        """
        raise BibFilterError(self.name(), 'BibFilter subclasses must reimplement action()!')


    def prerun(self, bibolamazifile):
        """
        This function gets called immediately before the filter is run, after any
        preceeding filters have been executed.

        It is not very useful if the :py:meth:`action()` is
        :py:const:`BibFilter.BIB_FILTER_BIBOLAMAZIFILE`, but it can prove useful for
        filters with action :py:const:`BibFilter.BIB_FILTER_SINGLE_ENTRY`, if any sort of
        pre-processing task should be done just before the actual filtering of the data.

        The default implementation does nothing.
        """
        return
    

    def filter_bibentry(self, x):
        """
        The main filter function for filters that filter the data entry by entry.
        
        If the subclass' :py:meth:`action()` function returns
        :py:const:`BibFilter.BIB_FILTER_SINGLE_ENTRY`, then the subclass must reimplement
        this function. Otherwise, this function is never called.

        The object `x` is a :py:class:`pybtex.database.Entry` object instance, which
        should be updated according to the filter's action and purpose.

        The return value of this function is ignored. Subclasses should report warnings
        and logging through :py:data:`core.blogger.logger` and should raise errors as
        :py:class:`BibFilterError` (preferrably, a subclass). Other raised exceptions will
        be interpreted as internal errors and will open a debugger.
        """
        raise BibFilterError(self.name(), 'filter_bibentry() not implemented !')

    def filter_bibolamazifile(self, x):
        """
        The main filter function for filters that filter the data entry by entry.
        
        If the subclass' :py:meth:`action()` function returns
        :py:const:`BibFilter.BIB_FILTER_SINGLE_ENTRY`, then the subclass must reimplement
        this function. Otherwise, this function is never called.

        The object `x` is a :py:class:`~core.bibolamazifile.BibolamaziFile` object
        instance, which should be updated according to the filter's action and purpose.

        The return value of this function is ignored. Subclasses should report warnings
        and logging through :py:data:`core.blogger.logger` and should raise errors as
        :py:class:`BibFilterError` (preferrably, a subclass). Other raised exceptions will
        be interpreted as internal errors and will open a debugger.
        """
        raise BibFilterError(self.name(), 'filter_bibolamazifile() not implemented !')


    def requested_cache_accessors(self):
        """
        This function should return a list of :py:class:`bibusercache.BibUserCacheAccessor`
        class names of cache objects it would like to use. The relevant caches are then
        collected from the various filters and automatically instantiated and initialized.

        The default implementation of this function returns an empty list. Subclasses
        should override if they want to access the bibolamazi cache.
        """
        return []




    # --------------------------------------------------------------------------


    def name(self):
        """
        Returns the name of the filter as it was invoked in the bibolamazifile. This might
        be with, or without, the filterpackage. This information should
        be only used for reporting purposes and might slightly vary.

        If the filter was instantiated manually, and :py:meth:`setInvokationName()` was
        not called, then this function returns the class name.

        The subclass should not reimplement this function unless it really really really
        *really* feels it needs to.
        """
        return self._filtername

    def setInvokationName(self, filtername):
        """
        Called internally by bibolamazifile, so that :py:meth:`name()` returns the name by
        which this filter was invoked.

        This function sets exactly what :py:meth:`name()` will return. Subclasses should
        not reimplement, the default implementation should suffice.
        """
        self._filtername = filtername



    def setBibolamaziFile(self, bibolamazifile):
        """
        Remembers `bibolamazifile` as the :py:class:`~core.bibolamazifile.BibolamaziFile`
        object that we will be acting on.

        There's no use overriding this. When writing filters, there's also no need calling
        this explicitly, it's done in :py:class:`~core.bibolamazifile.BibolamaziFile`.
        """
        self._bibolamazifile = bibolamazifile;

    def bibolamaziFile(self):
        """
        Get the :py:class:`~core.bibolamazifile.BibolamaziFile` object that we are acting
        on. (The one previously set by :py:meth:`setBibolamaziFile()`.)

        There's no use overriding this.
        """
        return self._bibolamazifile;
    
    def cacheAccessor(self, klass):
        """
        A shorthand for calling the :py:meth:`cacheAccessor()` method of the bibolamazi
        file returned by :py:meth:`bibolamaziFile()`.
        """
        return self.bibolamaziFile().cacheAccessor(klass)


    def getRunningMessage(self):
        """
        Return a nice message to display when invoking the fitler. The default
        implementation returns :py:meth:`name()`. Define this to whatever you want in your
        subclass to describe what you're doing. The core bibolamazi program displays this
        information to the user as it runs the filter.
        """
        return self.name();


    # convenience functions, no need to (i.e. should not) override
    @classmethod
    def getHelpAuthor(cls):
        """
        Convenience function that returns :py:data:`helpauthor`, with whitespace stripped. 
        Use this when getting the contents of the helpauthor text.

        There's no need to (translate: you should not) reimplement this function in your
        subclass.
        """
        return cls.helpauthor.strip();

    @classmethod
    def getHelpDescription(cls):
        """
        Convenience function that returns :py:data:`helpdescription`, with whitespace
        stripped. Use this when getting the contents of the helpdescription text.

        There's no need to (translate: you should not) reimplement this function in your
        subclass.
        """
        return cls.helpdescription.strip();

    @classmethod
    def getHelpText(cls):
        """
        Convenience function that returns :py:data:`helptext`, with whitespace stripped. 
        Use this when getting the contents of the helptext text.

        There's no need to (translate: you should not) reimplement this function in your
        subclass.
        """
        return cls.helptext.strip();
    


