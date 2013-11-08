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

    def cache_for(self, namespace):
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
            return self._bibolamazifile.cache_for(namespace)
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
    



class EnumArgType:
    def __init__(self, listofvalues):
        self.listofvalues = listofvalues
