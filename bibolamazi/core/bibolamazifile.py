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


"""
The Main bibolamazifile module: this contains the :py:class:`BibolamaziFile` class
definition.
"""


import re
import io
import sys
import os
import os.path
import codecs
import shlex
import urllib
import cPickle as pickle
from datetime import datetime
import logging

import bibolamazi.init

import pybtex.database
import pybtex.database.input.bibtex as inputbibtex
import pybtex.database.output.bibtex as outputbibtex
from pybtex.utils import OrderedCaseInsensitiveDict

from bibolamazi.core import butils
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibusercache import BibUserCache, BibUserCacheDic, BibUserCacheList
from bibolamazi.core.bibfilter import factory

logger = logging.getLogger(__name__)


class BibolamaziFileParseError(BibolamaziError):
    def __init__(self, msg, fname=None, lineno=None):
        where = None
        if (fname is not None):
            where = fname
            if (lineno is not None):
                where += ", line %d" %(lineno)
                
        BibolamaziError.__init__(self, msg, where=where)


class NotBibolamaziFileError(BibolamaziFileParseError):
    """
    This error is raised to signify that the file specified is not a bibolamazi
    file---most probably, it does not contain a valid configuration section.
    """
    def __init__(self, msg, fname=None, lineno=None):
        BibolamaziFileParseError.__init__(self, msg=msg, fname=fname, lineno=lineno)

class BibolamaziBibtexSourceError(BibolamaziError):
    def __init__(self, msg, fname=None):
        where = fname

        BibolamaziError.__init__(self, msg, where=where)


def _repl(s, dic):
    for (k,v) in dic.iteritems():
        s = re.sub(k, v, s)
    return s





class BibolamaziFileCmd:
    """
    A command in the bibolamazi file configuration

    Stores the command name (e.g. 'src' or 'filter'), additional text (the options), line
    number information and possible additional information.

    Object Properties:
    
      - `cmd`: the command name. Currently this is 'src' or 'filter'

      - `text`: the text following the command. This is e.g. the sources list, or a filter
        name followed by options. In general, it is anything following the 'src:' or
        'filter:' commands.

      - `lineno`: the line number at which this command is specified in the bibolamazi
        file, relative to the top of the file. The first line of the file is line number
        1.

      - `linenoend`: the line number at which the command ends.

      - `info`: a dictionary with possible additional information which is available at
        parse time. For example, the filter name for 'filter' commands is stored when
        parsing commands.

    See also :py:meth:`bibolamazifile.configCmds()`.
    """
    def __init__(self, cmd=None, text="", lineno=-1, linenoend=-1, info={}):
        """
        Construct a `BibolamaziFileCmd` with the given `cmd`, `text`, `lineno`, `linenoend`
        and `info`.
        """
        self.cmd = cmd
        self.text = text
        self.lineno = lineno
        self.linenoend = linenoend
        self.info = info

    def __repr__(self):
        return ("%s(" %(self.__class__.__name__)   +
                ", ".join([
                    k+"="+repr(getattr(self,k))
                    for k in ('cmd','text','lineno','linenoend','info')
                    ])   +
                ")"
                )


CONFIG_BEGIN_TAG = '%%%-BIB-OLA-MAZI-BEGIN-%%%'
"""
The line which defines the beginning of a config section in a bibolamazi file.
"""
CONFIG_END_TAG = '%%%-BIB-OLA-MAZI-END-%%%'
"""
The line which defines the end of a config section in a bibolamazi file.
"""

AFTER_CONFIG_TEXT = """\
%
%
% ALL CHANGES BEYOND THIS POINT WILL BE LOST NEXT TIME BIBOLAMAZI IS RUN.
%


%
% This file was generated by BIBOLAMAZI __BIBOLAMAZI_VERSION__ on __DATETIME_NOW__
%
%     https://github.com/phfaist/bibolamazi
%
% Bibolamazi collects bib entries from the sources listed in the configuration section
% above, and merges them all into this file while applying the defined filters with
% the given options. Your sources will not be altered.
%
% Any entries ABOVE the configuration section will be preserved as is, which means that
% if you don't want to install bibolamazi or if it not installed, and you want to add
% a bibliographic entry to this file, add it AT THE TOP OF THIS FILE.
%
%





"""
"""
Some text which is inserted immediately after the config section when saving
bibolamazi files. Includes a warning about losing any changes.
"""# docstring

                    
# this is fixed to utf-8. No alternatives, sorry.
BIBOLAMAZI_FILE_ENCODING = 'utf-8'
"""
The encoding used to read and write bibolamazi files. Don't change this.
"""


BIBOLAMAZIFILE_INIT = 0
"""
Bibolamazi file load state: freshly initialized, no data read. See doc for
:py:class:`BibolamaziFile`.
"""
BIBOLAMAZIFILE_READ = 1
"""
Bibolamazi file load state: data read, not parsed. See doc for
:py:class:`BibolamaziFile`.
"""
BIBOLAMAZIFILE_PARSED = 2
"""
Bibolamazi file load state: data read and parsed, filters instanciated but no sources
loaded. See doc for :py:class:`BibolamaziFile`.
"""
BIBOLAMAZIFILE_LOADED = 3
"""
Bibolamazi file load state: data read and parsed, filters instanciated and data from
sources loaded. See doc for :py:class:`BibolamaziFile`.
"""



_key_duplsuffix = '.dupl.'
_rx_repl_key_duplsuffix = re.compile(r'($|'+re.escape(_key_duplsuffix)+r'(?P<num>\d+)$)',
                                     flags=re.IGNORECASE)



class BibolamaziFile(object):
    """
    Represents a Bibolamazi file.

    This class provides an API to read and parse bibolamazi files, as well as load data
    defined in its configuration section and interact with its filters.

    A `BibolamaziFile` object may be in different load states:

      - :py:const:`BIBOLAMAZIFILE_INIT`: The `BibolamaziFile` object is initialized to an
        empty state. The file name (:py:meth:`fname()`) may be set already, but is `None`
        by default.

      - :py:const:`BIBOLAMAZIFILE_READ`: Data has been read from a given file, but not
        parsed. You may call certain methods such as :py:meth:`rawHeader()` or
        :py:meth:`configData()`, but e.g. :py:meth:`configCmds()` will return an invalid
        value.

      - :py:const:`BIBOLAMAZIFILE_PARSED`: Data has been read from a bibolamazi file and
        parsed, and filter objects have been instanciated. Methods such as
        :py:meth:`filters()` or :py:meth:`sourceLists()` may be called.

      - :py:const:`BIBOLAMAZIFILE_LOADED`: The bibolamazi file has been read and parsed,
        filter objects have been instanciated and bibtex data from the sources has been
        loaded. This is the "maximally loaded" state.

    You may query the load state with :py:meth:`getLoadState()` and load a bibolamazi file
    either from the constructor or by calling explicitly :py:meth:`load()`. Some methods
    on this object may only be called if the object has reached a certain load
    state. These methods are documented as such.

    The bibliography database is accessed with :py:meth:`bibliographyData()`. You may
    change the entries in the database via direct access (using the `pybtex` API), or
    using the method :py:meth:`setEntries()`.

    To create a new bibolamazi file template, you may specify `create=True` to the
    constructor with a valid file name, and save the object.
    """
    def __init__(self, fname=None, create=False,
                 load_to_state=BIBOLAMAZIFILE_LOADED,
                 use_cache=True,
                 default_cache_invalidation_time=None):
        """
        Create a BibolamaziFile object.

        If `fname` is provided, the file is fully loaded (unless `create` is also
        provided).

        If `create` is given and set to `True`, then an empty template is loaded and the
        internal file name is set to `fname`. The internal state will be set to
        :py:const:`BIBOLAMAZIFILE_LOADED` and calling :py:meth:`saveToFile()` will result
        in writing this template to the file `fname`.

        If `load_to_state` is given, then the file is only loaded up to the given state.
        See :py:meth:`load()` for more details. The state should be one of
        :py:const:`BIBOLAMAZIFILE_INIT`, :py:const:`BIBOLAMAZIFILE_READ`,
        :py:const:`BIBOLAMAZIFILE_PARSED` or :py:const:`BIBOLAMAZIFILE_LOADED`.

        If `use_cache` is `True` (default), then when loading this file, we'll attempt to
        load a corresponding cache file if it exists. Note that even if `use_cache` is
        `False`, then cache will still be *written* when calling :py:meth:`saveToFile()`.

        If `default_cache_invalidation_time` is given, then the default cache invalidation
        time is set before loading the cache.
        """
        
        logger.debug("Opening bibolamazi file `%s'" %(fname))
        self._fname = None
        self._dir = None
        self._use_cache = use_cache

        if (create):
            self._init_empty_template()
            self._fname = fname
            self._dir = os.path.dirname(os.path.realpath(fname))
        elif (fname):
            # read the file, load settings
            self.load(fname=fname, to_state=min(load_to_state, BIBOLAMAZIFILE_PARSED))
            # set the default cache invalidation time to the given value, before we load
            # all the data and cache.
            if default_cache_invalidation_time is not None:
                self.setDefaultCacheInvalidationTime(default_cache_invalidation_time)
            # now load the data, if required.
            if (load_to_state > BIBOLAMAZIFILE_PARSED):
                self.load(to_state=load_to_state)
        else:
            logger.debug("No file given. Don't forget to set one with load()")

            
    # Note: the name "loadState()" would have been ambiguous: it could be understood
    # as an imperative
    def getLoadState(self):
        """
        Returns the state of the `BibolamaziFile` object. One of :py:const:`BIBOLAMAZIFILE_INIT`,
        :py:const:`BIBOLAMAZIFILE_READ`, :py:const:`BIBOLAMAZIFILE_PARSED`, or
        :py:const:`BIBOLAMAZIFILE_LOADED`.
        """
        return self._load_state

    def reset(self):
        """
        Reset the current object to an empty state and unset the file name. This will reset the
        object to the state :py:const:`BIBOLAMAZIFILE_INIT`.
        """
        self.load(fname=None, to_state=BIBOLAMAZIFILE_INIT)

    def load(self, fname=[], to_state=BIBOLAMAZIFILE_LOADED):
        """
        Load the given file into the current object.

        If `fname` is `None`, then reset the object to an empty state. If `fname` is not
        given or an empty ``list``, then use any previously loaded fname and its state.

        This function may be called several times with different states to incrementally
        load the file, for example::

            bibolamazifile.reset()
            # load up to 'parsed' state
            bibolamazifile.load(fname="somefile.bibolamazi.bib", to_state=BIBOLAMAZIFILE_PARSED)
            # continue loading up to fully 'loaded' state
            bibolamazifile.load(fname="somefile.bibolamazi.bib", to_state=BIBOLAMAZIFILE_LOADED)

        If `to_state` is given, will only attempt to load the file up to that state. This
        can be useful, e.g., in a config editor which needs to parse the sections of the
        file but does not need to worry about syntax errors. The state should be one of
        :py:const:`BIBOLAMAZIFILE_INIT`, :py:const:`BIBOLAMAZIFILE_READ`,
        :py:const:`BIBOLAMAZIFILE_PARSED` or :py:const:`BIBOLAMAZIFILE_LOADED`.
        """
        
        if (isinstance(fname, list) and not fname):
            # fname=[], so keep old file name and properties.
            pass
        else:
        #if (fname or not isinstance(fname, list)):
            # required to replace current file, if one open
            self._fname = fname
            self._dir = os.path.dirname(os.path.realpath(fname)) if fname is not None else None
            self._load_state = BIBOLAMAZIFILE_INIT
            self._header = None
            self._config = None
            self._config_data = None
            self._startconfigdatalineno = None
            self._rest = None
            self._cmds = None
            self._sources = None
            self._source_lists = []
            self._filters = []
            self._cache_accessors = {} # dict { class-type: class-instance }
            self._bibliographydata = None
            self._user_cache = BibUserCache(cache_version=butils.get_version())
            
        if (to_state >= BIBOLAMAZIFILE_READ  and  self._load_state < BIBOLAMAZIFILE_READ):
            try:
                with codecs.open(self._fname, 'r', encoding=BIBOLAMAZI_FILE_ENCODING) as f:
                    logger.longdebug("File "+repr(self._fname)+" opened.")
                    self._read_config_stream(f, self._fname)
            except IOError as e:
                raise BibolamaziError(u"Can't open file `%s': %s" %(self._fname, unicode(e)))

        if (to_state >= BIBOLAMAZIFILE_PARSED  and  self._load_state < BIBOLAMAZIFILE_PARSED):
            self._parse_config()

        if (to_state >= BIBOLAMAZIFILE_LOADED  and  self._load_state < BIBOLAMAZIFILE_LOADED):
            self._load_contents()

        return True


    def fname(self):
        """
        Returns the file name this object refers to.

        If the state is any other than :py:const:`BIBOLAMAZIFILE_INIT`, then this function
        will never return `None`.
        """
        return self._fname

    def fdir(self):
        """
        Returns the directory name in which this bibolamazi file resides, always as a full
        path (using `os.path.realpath`, resolving symlinks). The value is cached, so you
        may call this function several times with little performance overhead.

        If :py:meth:`fname()` is `None` (this is only possible if the load state is
        :py:const:`BIBOLAMAZIFILE_INIT`), then `None` is returned.
        """
        return self._dir

    def rawHeader(self):
        """
        Return any content above the configuration section.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return self._header

    def rawConfig(self):
        """
        Return the raw configuration section. The returned value will NOT have the leading
        percent signs removed.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return self._config

    def rawRest(self):
        """
        Return all the contents after the config section at the moment the file was read from
        the disk. This includes the begin and end config section tags
        (:py:const:`CONFIG_BEGIN_TAG` and :py:const:`CONFIG_END_TAG`).

        Any changes to the bibliography data will not be reflected here, even if you call
        :py:meth:`saveToFile()`.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return self._rest

    def configData(self):
        """
        Returns the configuration commands, with leading percent signs stripped, and without
        the begin and end tags.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return self._config_data

    def rawStartConfigDataLineNo(self):
        """
        Returns the line number on which the begin config tag :py:const:`CONFIG_BEGIN_TAG` is
        located. Line numbers start at 1 at the top of the file like in any reasonable
        editor.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return self._startconfigdatalineno

    def fileLineNo(self, configlineno):
        """
        Utility to convert config line number to file line number

        Returns the line number in the bibolamazi file corresponding to the config line
        number `configlineno`. The `configlineno` refers to the line number INSIDE the
        config section, where line number 1 is right after the begin config tag
        :py:const:`CONFIG_BEGIN_TAG`.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return configlineno + self._startconfigdatalineno

    def configLineNo(self, filelineno):
        """
        Utility to convert file line number to config line number

        Returns the line number in the config data corresponding to line `filelineno` in
        the file. Opposite of :py:meth:`fileLineNo()`.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_READ`.
        """
        return filelineno - self._startconfigdatalineno

    def configCmds(self):
        """
        Return a list of parsed commands from the configuration section.

        This returns a list of :py:class:`BibolamaziFileCmd` objects.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_PARSED`.
        """
        return self._cmds

    def sourceLists(self):
        """
        Return a list of source lists, in the order they are specified in the configuration
        section.

        Each item in the returned list is itself a list of alternative sources to
        consider.

        This may be called in the state :py:const:`BIBOLAMAZIFILE_PARSED`.
        """
        return self._source_lists

    def sources(self):
        """
        Return a list of sources which have been read.

        This is a list of strings. Each item in the returned list is one of the items in
        the corresponding list from :py:meth:`sourceLists()` (the one that was actually
        found and read). If no corresponding item in `sourceLists()` was readable, then
        the corresponding item in this list is `None`. For example::

          # suppose that we have the following instructions in the bibolamazi file:
          #
          #     src: src1.bib
          #     src: a.bib b.bib c.bib
          #     src: x/x.bib y/y.bib
          #
          # we would then have:
          #
          f.sourceLists() == [["src1.bib"], ["a.bib", "b.bib", "c.bib"], ["x/x.bib", "y/y.bib"]]

          # suppose that "src1.bib" exists, "a.bib" doesn't exist but "b.bib" exists, and neither
          # "x/x.bib" nor "y/y.bib" don't exist.
          #
          # Then, after loading this object, we get:
          #
          f.sources() == ["src1.bib", "b.bib", None]
        
        This function may be called in the state :py:const:`BIBOLAMAZIFILE_LOADED`.
        """
        return self._sources

    def filters(self):
        """
        Return a list of filter instances

        This returns the list of all filter commands given in the bibolamazi config
        section. The instances have already been instanciated with the proper options. The
        order of this list is exactly the order of the filters in the config section.

        If in the config section the same filter is invoked several times, then separate
        instances are returned in this list with the appropriate ordering, as you'd
        expect.
        """
        return self._filters

    def bibliographyData(self):
        """
        Return the `pybtex.database.BibliographyData` object which stores all the
        bibliography entries.

        This object is only instanciated and initialized once in the
        :py:const:`BIBOLAMAZIFILE_LOADED` state. If ``getLoadState() != BIBOLAMAZIFILE_LOADED``,
        then this function returns `None`.
        """
        return self._bibliographydata

    def bibliographydata(self):
        """
        .. deprecated:: 2.0
           Use `bibliographyData()` instead!
        """
        butils.warn_deprecated("BibolamaziFile", "bibliographydata()", "bibliographyData()", __name__)
        return self.bibliographyData()

    def cacheFileName(self):
        """
        The file name where the cache will be stored. You don't need to access this
        directly, the cache will be loaded and saved automatically.

        Filters should only access the cache through cache accessors. See
        `cacheAccessor()`.
        """
        return self._fname + '.bibolamazicache'
        

    def cacheAccessor(self, klass):
        """
        Returns the cache accessor instance corresponding to the given class.

        See documentation of :py:mod:`bibolamazi.core.bibusercache` for more information
        about the bibolamazi cache.

        If the cache accessor was not loaded, then `None` is returned.
        """
        return self._cache_accessors.get(klass, None)
        

    def setDefaultCacheInvalidationTime(self, time_delta):
        """
        A timedelta object giving the amount of time for which data in cache is consdered
        valid (by default).

        Note that this function should be called BEFORE the data is loaded. If you just
        call, for example the default constructor, this might be too late already. If you
        use the `load()` function, set the default cache invalidation time before you load
        up to the state `BIBOLAMAZIFILE_LOADED`.

        Note that you may also use the option in the constructor
        `default_cache_invalidation_time`, which has the same effect as this funtion
        called at the appropriate time.
        """

        # Note that we set the invalidation anyway, even if we have
        # `self._use_cache==False`, because in that case the cache is still saved.

        if not self._user_cache:
            logger.warning('BibolamaziFile.setDefaultCacheInvalidationTime(): Invalid cache object')
            return

        self._user_cache.setDefaultInvalidationTime(time_delta)

    def setConfigData(self, configdata):
        """
        Store the given data `configdata` in memory as the configuration section of this file.
        
        This function cleanifies the `configdata` a bit by adding leading percent signs
        and forcing a final newline, adds the config section begin and end tags, and then
        directly calls :py:meth:`setRawConfig()`.
        """
        # prefix every line by a percent sign.
        config_block = re.sub(r'^', '% ', configdata, flags=re.MULTILINE)

        # force ending in '\n' (but don't duplicate existing '\n')
        if (not len(config_block) or config_block[-1] != '\n'):
            config_block += '\n'

        # add start and end bibolamazi config section tags.
        config_block = CONFIG_BEGIN_TAG + '\n' + config_block + CONFIG_END_TAG + '\n'

        self.setRawConfig(config_block)


    def setRawConfig(self, configblock):
        """
        Store the given `configblock` in memory as the raw configuration section of the
        bibolamazi file. We must be at least in state :py:const:`BIBOLAMAZIFILE_READ` to
        call this function; this function will also reset to state back to
        :py:const:`BIBOLAMAZIFILE_READ` (as the configuration might have changed).
        
        Note that `configblock` is expected to start and end with the appropriate config
        section tags (:py:const:`CONFIG_BEGIN_TAG` and :py:const:`CONFIG_END_TAG`).
        
        After calling this function, :py:meth:`configData()` will return the new
        configuration data. Call :py:meth:`load()` to re-instanciate filters and re-load
        sources.
        """
        if (self._load_state < BIBOLAMAZIFILE_READ):
            raise BibolamaziError("Can only setConfigSection() if we have read a file already!")

        self._config = configblock
        self._config_data = self._config_data_from_block(configblock)
        # in case we were in a more advanced state, reset to READ state, because config has changed.
        self._load_state = BIBOLAMAZIFILE_READ


    def resolveSourcePath(self, path):
        """
        Resolves a path (for example corresponding to a source file) to an absolute file
        location.

        This function expands '~/foo/bar' to e.g. '/home/someone/foo/bar'; it also expands
        shell variables, e.g. '$HOME/foo/bar' or '${MYBIBDIR}/foo/bar.bib'.

        If the path is relative, it is made absolute by interpreting it as relative to the
        location of this bibolamazi file (see :py:meth:`fdir()`).

        Note: `path` should not be an URL.
        """
        # expand ~/foo/bar, $HOME/foo/bar as well as ${MYBIBDIR}/foo/bar.bib
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        # if the path is relative, make it absolute. I'ts relative to the bibolamazi file.
        # (note: `os.path.join(a, b)` will ignore `a` if `b` is absolute)
        return os.path.join(self._dir, path)


    def _init_empty_template(self):

        # provide us an initialized instance
        self.load(None, to_state=BIBOLAMAZIFILE_INIT)

        self._header = _TEMPLATE_HEADER
        self._config = _TEMPLATE_CONFIG
        self._config_data = self._config_data_from_block(_TEMPLATE_CONFIG)
        self._rest = ''#_TEMPLATE_REST

        # store raw cmds
        self._cmds = []

        # parse commands
        self._sources = []
        self._source_lists = []
        self._filters = []
        self._cache_accessors = {}

        # cheat, we've loaded it manually
        self._load_state = BIBOLAMAZIFILE_LOADED

        self._bibliographydata = pybtex.database.BibliographyData()

        logger.longdebug('done with empty template init!')


    def _config_data_from_input_lines(self, inputconfigdata):
        """
        Simply strips initial %'s on each line of `inputconfigdata`.
        """

        return re.sub(r'^\%[ \t]?', '', inputconfigdata, flags=re.MULTILINE)

    def _config_data_from_block(self, inputconfigdata):
        """
        Detects and removes starting and ending config tags, and then filters each
        line through `_config_data_from_input_lines()`.
        """

        data_lines = []
        
        sio = io.StringIO(unicode(inputconfigdata))
        is_first = True
        for line in sio:
            if (is_first):
                is_first = False
                if (not line.startswith(CONFIG_BEGIN_TAG)):
                    logger.warning("Use of _config_data_from_block() *without* BEGIN/END tags !")
                else:
                    continue
            data_lines.append(self._config_data_from_input_lines(line))

        return "".join(data_lines)

        
    def _raise_parse_error(self, msg, lineno):
        raise BibolamaziFileParseError(msg, fname=self._fname, lineno=lineno)


    def _read_config_stream(self, stream, streamfname=None):

        ST_HEADER = 0
        ST_CONFIG = 1
        ST_REST = 2

        state = ST_HEADER

        content = {
            ST_HEADER: u"",
            ST_CONFIG: u"",
            ST_REST: u""
            }
        config_block_lines = []

        lineno = 0
        self._startconfigdatalineno = None

        for line in stream:
            lineno += 1
            
            if (state == ST_HEADER and line.startswith(CONFIG_BEGIN_TAG)):
                state = ST_CONFIG
                content[ST_CONFIG] += line
                self._startconfigdatalineno = lineno
                continue

            if (state == ST_CONFIG and line.startswith(CONFIG_END_TAG)):
                content[ST_CONFIG] += line
                state = ST_REST
                continue

            if (state == ST_CONFIG):
                # remove leading % signs
                #logger.debug("adding line to config_block: "+line)
                cline = line
                if (len(cline) and cline[-1] == '\n'):
                    cline = cline[:-1]
                config_block_lines.append(cline)

            content[state] += line

        if (state != ST_REST):
            # file is not a bibolamazi file--no config section found.
            # error lineno is last line of file.
            raise NotBibolamaziFileError("Not a bibolamazi file--no config section found.",
                                         fname=self._fname, lineno=lineno)

        config_block = "\n".join(config_block_lines)

        # save the splitted data into these data structures.
        self._header = content[ST_HEADER]
        self._config = content[ST_CONFIG]
        self._config_data = self._config_data_from_input_lines(config_block)
        self._rest = content[ST_REST]

        logger.longdebug(("Parsed general bibolamazifile structure: len(header)=%d"+
                      "; len(config)=%d; len(config_data)=%d; len(rest)=%d") %
                     ( len(self._header),
                       len(self._config),
                       len(self._config_data),
                       len(self._rest) ) )


        logger.longdebug("config data is"+ "\n--------------------------------\n"
                     +self._config_data+"\n--------------------------------\n")

        self._load_state = BIBOLAMAZIFILE_READ
        return True

    def _parse_config(self):
        # now, parse the configuration.
        self._config_data = self._config_data_from_block(self._config)
        configstream = io.StringIO(unicode(self._config_data))
        cmds = []
        emptycmd = BibolamaziFileCmd(cmd=None, text="", lineno=-1, linenoend=-1, info={})
        latestcmd = emptycmd
        # all 'src:' commands must be BEFORE any 'filter:' commands. `current_section`
        # indicates in which command block we are ('src' or 'filter')
        current_section = 'src'
        def complete_cmd():
            if (latestcmd.cmd is not None):
                cmds.append(latestcmd)

        thislineno = self._startconfigdatalineno
        for cline in configstream:
            thislineno += 1

            if (re.match(r'^\s*%%', cline)):
                # ignore comments
                continue
            
            if (re.match(r'^\s*$', cline)):
                # empty line -> forces the state back to an empty state. We now expect a
                # new 'src:' or 'filter:' keyword
                complete_cmd()
                latestcmd = emptycmd
                continue

            # try to match to a new command
            mcmd = re.match(r'^\s{0,1}(src|filter):\s*', cline)
            if (not mcmd):
                if (latestcmd.cmd is None):
                    # no command
                    self._raise_parse_error("Expected a bibolamazi command",
                                            lineno=thislineno)
                # simply continue current cmd
                latestcmd.text += cline
                latestcmd.linenoend = thislineno
                continue

            # we have completed the current cmd
            complete_cmd()
            latestcmd = emptycmd
            # start new cmd
            cmd = mcmd.group(1)
            rest = cline[mcmd.end():]
            info = { }
            if (cmd == "filter"):
                current_section = 'filter'
                # extract filter name
                mfiltername = re.match('^\s*(?P<filtername>(?:[\w.]+:)?\w+)(\s|$)', rest)
                if (not mfiltername):
                    self._raise_parse_error("Expected filter name", lineno=thislineno)
                filtername = mfiltername.group('filtername')
                rest = rest[mfiltername.end():]
                info['filtername'] = filtername
            if cmd == "src" and current_section == 'filter':
                self._raise_parse_error("'src:' commands must preceed any 'filter:' commands", lineno=thislineno)

            # and start cumulating stuff
            latestcmd = BibolamaziFileCmd(cmd=cmd, text=rest, lineno=thislineno, linenoend=thislineno, info=info)

        # complete the last cmd
        complete_cmd()

        # store raw cmds
        self._cmds = cmds

        # parse commands
        self._sources = []
        self._source_lists = []
        self._filters = []
        self._cache_accessors = {}
        for cmd in cmds:
            if (cmd.cmd == "src"):
                thesrc_list = shlex.split(cmd.text)
                self._source_lists.append(thesrc_list)
                self._sources.append('') # this will be set later to which source in the
                #                          list was actually accessed.
                logger.debug("Added source list %r" % (thesrc_list))
                continue
            if (cmd.cmd == "filter"):
                filname = cmd.info['filtername']
                filoptions = cmd.text
                try:
                    filterinstance = factory.make_filter(filname, filoptions)
                    filterinstance.setBibolamaziFile(self)
                    filterinstance.setInvokationName(filname)
                    self._filters.append(filterinstance)
                except factory.NoSuchFilter as e:
                    self._raise_parse_error(str(e), lineno=cmd.lineno)
                except factory.NoSuchFilterPackage as e:
                    self._raise_parse_error(str(e), lineno=cmd.lineno)
                except factory.FilterError as e:
                    import traceback
                    logger.debug("FilterError:\n" + traceback.format_exc())
                    self._raise_parse_error(unicode(e),
                                            lineno=cmd.lineno)

                # see if we have to register a new cache accessor
                for req_cache in list(filterinstance.requested_cache_accessors()):
                    if req_cache not in self._cache_accessors:
                        # construct a cache accessor for this cache.
                        try:
                            cache_accessor = req_cache(bibolamazifile=self)
                            self._cache_accessors[req_cache] = cache_accessor
                        except Exception as e:
                            ## ### TODO: ADD STACK TRACE IN VERBOSE OUTPUT
                            raise BibolamaziError(
                                (u"Error in cache %s: Exception while instantiating the class:\n"
                                 u"%s: %s")
                                %( req_cache.__name__, e.__class__.__name__, unicode(e) )
                                )
                        
                logger.debug("Added filter '"+filname+"': `"+filoptions.strip()+"'")
                continue

            self._raise_parse_error("Unknown command: `%s'" %(cmd.cmd),
                                    lineno=cmd.lineno)

        self._load_state = BIBOLAMAZIFILE_PARSED

        logger.longdebug("done with _parse_config()")
        return True


    def _load_contents(self):
        """
        Load the source data and the cache.
        """

        # Load the sources
        # ----------------

        self._bibliographydata = None

        if (not len(self._source_lists)):
            logger.warning("File `%s': No source files specified. You need source files to provide bib entries!"
                           %(self._fname))

        # now, populate all bibliographydata.
        for k in range(len(self._source_lists)):
            srclist = self._source_lists[k]
            src = self._populate_from_srclist(srclist)
            self._sources[k] = src


        # Now, try to load the cache
        # --------------------------
        if self._use_cache:
            # then, try to load the cache if possible
            cachefname = self.cacheFileName()
            try:
                with open(cachefname, 'rb') as f:
                    logger.longdebug("Reading cache file %s" %(cachefname))
                    self._user_cache.loadCache(f)
            except (IOError, EOFError,):
                logger.debug("Cache file `%s' nonexisting or not readable." %(cachefname))
                pass
        else:
            logger.debug("As requested, I have not attempted to load any existing cache file.")

        # Finally, initialize the cache.
        # ------------------------------

        # this should be done independently of whether we are loading/saving cache and/or
        # if the cache load succeeded. Remember that the cache is always there, and
        # filters always use it. `self._use_cache` only tells us whether to load some
        # initial data.

        for (cacheaccessor, cacheaccessorinstance) in self._cache_accessors.iteritems():
            #
            # Ensure the existance of the cache dictionary instance in the cache
            #
            self._user_cache.cacheFor(cacheaccessorinstance.cacheName())
            #
            # Set the accessor's pointer to the cache object
            #
            cacheaccessorinstance.setCacheObj(cache_obj=self._user_cache)
            #
            # and initialize the cache accessor
            #
            cacheaccessorinstance.initialize(self._user_cache)


        self._load_state = BIBOLAMAZIFILE_LOADED

        logger.longdebug('done with _load_contents!')
        return True


    def _populate_from_srclist(self, srclist):
        for src in srclist:
            # try to populate from this source
            ok = self._populate_from_src(src)
            if ok:
                return src
        logger.warning("Ignoring nonexisting source list: %s" %(", ".join(srclist)))
        return None

    def _populate_from_src(self, src):
        bib_data = None

        is_url = False
        if (re.match('^[A-Za-z0-9+_-]+://.*', src)):
            is_url = True
        
        if (not is_url):
            src = self.resolveSourcePath(src)

        # read data, decode it in the right charset
        data = None
        if is_url:
            logger.debug("Opening URL %r", src)
            try:
                f = urllib.urlopen(src)
                if (f is None):
                    return None
                data = butils.guess_encoding_decode(f.read())
                logger.longdebug(" ... successfully read %d chars from URL resouce." % len(data))
                f.close()
            except IOError:
                # ignore source, will have to try next in list
                return None
        else:
            logger.debug("Opening file %r", src)
            try:
                with open(src, 'r') as f:
                    data = butils.guess_encoding_decode(f.read())
            except IOError:
                # ignore source, will have to try next in list
                return None

        logger.info("Found Source: %s" %(src))

        try:
            # parse bibtex
            parser = inputbibtex.Parser()
            bib_data = None
            with io.StringIO(data) as stream:
                bib_data = parser.parse_stream(stream)

            if (self._bibliographydata is None):
                # initialize bibliography data
                self._bibliographydata = pybtex.database.BibliographyData()

            for key, entry in bib_data.entries.iteritems():
                if (key in self._bibliographydata.entries):
                    logger.warn('Repeated bibliography entry in other file: %s. Keeping first encountered entry.', key)
                    continue

                # TODO: Do this cleverly?
                #
                #if (key in self._bibliographydata.entries):
                #    oldkey = key
                #    duplcounter = 1
                #    while key in self._bibliographydata.entries:
                #        key = _rx_repl_key_duplsuffix.sub(_key_duplsuffix+str(duplcounter), key)
                #        duplcounter += 1
                #
                #    logger.warn('Repeated bibliography entry in other file: %s. Renamed duplicate occurence to %s.', oldkey, key)

                self._bibliographydata.add_entry(key, entry)

        except pybtex.database.BibliographyDataError as e:
            # We don't skip to next source, because we've encountered an error in the
            # BibTeX data itself: the file itself was properly found. So raise an error.
            raise BibolamaziBibtexSourceError(unicode(e), fname=src)

        return True



    def setBibliographyData(self, bibliographydata):
        """
        Set the `bibliographydata` database object directly.

        The object `bibliographydata` should be of instance
        :py:class:`pybtex.database.BibliographyData`.

        .. warning:: Filters should NOT set a different bibliographydata object:
                     caches might have kept a pointer to this object (see, for
                     example
                     :py:class:`~core.bibusercache.tokencheckers.EntryFieldsTokenChecker`). Please
                     use :py:meth:`setEntries()` instead.
        """
        self._bibliographydata = bibliographydata

    def setEntries(self, bibentries):
        """
        Replace all the entries in the current bibliographydata object by the given
        entries.

        Arguments:

            - `bibentries`: the new entries to set. `bibentries` should be an
              iterable of `(key, entry)` (or, more precisely, any valid argument
              for :py:meth:`pybtex.database.BibliographyData.add_entries()`).

        .. warning:: This will remove any existing entries in the database.

        This function alters the current :py:meth:`bibliographyData()` object,
        and does not replace it by a new object. (I.e., if you kept a reference
        to the `bibliographyData()` object, the reference is still valid after
        calling this function.)
        """

        # NOTE: Don't just set _bibliographydata to a new object, see warning in
        # doc of setBibliographyData().
        
        self._bibliographydata.entries = OrderedCaseInsensitiveDict()
        self._bibliographydata.add_entries(bibentries)



    def saveToFile(self):
        """
        Save the current bibolamazi file object to disk.

        This will write to the file :py:meth:`fname()` in order:

          - the raw header data (:py:meth:`rawHeader()`) unchanged

          - the config section text (:py:meth:`rawConfig()`) unchanged

          - the bibliography data contained in :py:meth:`bibliographyData`, saved in
            BibTeX format.

        A warning message is included after the config section that the remainder of the
        file was automatically generated.

        As the file `fname` is expected to already exist, it is always silently
        overwritten (so be careful).
        """
        with codecs.open(self._fname, 'w', BIBOLAMAZI_FILE_ENCODING) as f:
            f.write(self._header)
            f.write(self._config)
            f.write(_repl(AFTER_CONFIG_TEXT, {
                r'__BIBOLAMAZI_VERSION__': butils.get_version(),
                r'__DATETIME_NOW__': datetime.now().isoformat()
                }))

            if (self._bibliographydata):
                #
                # Pybtex 0.18: bibtex writer uses entry.original_type instead of
                # entry.type. (Why?? no idea)
                #
                # So if any filters changed entry.type, reflect that in
                # entry.original_type.
                for key, entry in self._bibliographydata.entries.iteritems():
                    entry.original_type = entry.type

                #
                # Write to bibtex output
                #
                w = outputbibtex.Writer()
                w.write_stream(self._bibliographydata, f)
            
            logger.info("Updated output file `"+self._fname+"'.")

        # if we have cache to save, save it
        if (self._user_cache and self._user_cache.hasCache()):
            cachefname = self.cacheFileName()
            try:
                with open(cachefname, 'wb') as f:
                    logger.debug("Writing cache to file %s" %(cachefname))
                    self._user_cache.saveCache(f)
            except IOError as e:
                logger.debug("Couldn't save cache to file `%s'." %(cachefname))
                pass

        




_TEMPLATE_HEADER = """\


.. Additionnal stuff here will not be managed by bibolamazi. It will also not be
.. overwritten. You can e.g. temporarily add additional references here if you
.. don't have bibolamazi installed.


"""

_TEMPLATE_CONFIG = """\
%%%-BIB-OLA-MAZI-BEGIN-%%%
%
% %% This bibliography database uses BIBOLAMAZI:
% %%
% %%     https://github.com/phfaist/bibolamazi
% %%
%
% %% This is the BIBOLAMAZI configuration section. Additional two leading
% %% percent signs indicate comments within the configuration.
%
% %% **** SOURCES ****
%
% %% The _first_ accessible file in _each_ source list will be read
%
% src:   <source file 1> [ <alternate source file 1> ... ]
% src:   <source file 2> [ ... ]
%
% %% Add additional sources here. Alternative files are useful, e.g., if the
% %% same file is to be accessed with different paths on different machines.
%
% %% **** FILTERS ****
%
% %% Specify filters here. Specify as many filters as you want, each with a
% %% `filter:' directive. See also `bibolamazi --list-filters' and
% %% `bibolamazi --help <filter>', or the "Help & Reference" page of the
% %% graphical interface.
%
% filter: filter_name  <filter options>
%
% %% Example:
% filter: arxiv -sMode=strip -sUnpublishedMode=eprint
%
% %% Finally, if your file is in a VCS, sort all entries by citation key so that
% %% you don't get huge file differences for each commit each time bibolamazi is
% %% run:
% filter: orderentries
%
%%%-BIB-OLA-MAZI-END-%%%
"""

