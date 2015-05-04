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
                
        BibolamaziError.__init__(self, msg, where=where);


class NotBibolamaziFileError(BibolamaziFileParseError):
    """
    This error is raised to signify that the file specified is not a bibolamazi
    file---most probably, it does not contain a valid configuration section.
    """
    def __init__(self, msg, fname=None, lineno=None):
        BibolamaziFileParseError.__init__(self, msg=msg, fname=fname, lineno=lineno);


def _repl(s, dic):
    for (k,v) in dic.iteritems():
        s = re.sub(k, v, s);
    return s;





class BibolamaziFileCmd:
    def __init__(self, cmd=None, text="", lineno=-1, linenoend=-1, info={}):
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


CONFIG_BEGIN_TAG = '%%%-BIB-OLA-MAZI-BEGIN-%%%';
CONFIG_END_TAG = '%%%-BIB-OLA-MAZI-END-%%%';

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





""";

                    
# this is fixed to utf-8. No alternatives, sorry.
BIBOLAMAZI_FILE_ENCODING = 'utf-8';


BIBOLAMAZIFILE_INIT = 0
BIBOLAMAZIFILE_READ = 1
BIBOLAMAZIFILE_PARSED = 2
BIBOLAMAZIFILE_LOADED = 3



_key_duplsuffix = '.dupl.'
_rx_repl_key_duplsuffix = re.compile(r'($|'+re.escape(_key_duplsuffix)+r'(?P<num>\d+)$)',
                                     flags=re.IGNORECASE)



class BibolamaziFile(object):
    """
    Represents a Bibolamazi file.

    This class provides an API to read and parse bibolamazi files, as well as load data
    defined in its configuration section and interact with its filters.

    Filter instances are automatically created upon loading, etc.

    .......... TODO: MORE DOC ............

    .......... TODO: DOCUMENT MEMBERS ...........
    
    """
    def __init__(self, fname=None, create=False,
                 load_to_state=BIBOLAMAZIFILE_LOADED,
                 use_cache=True,
                 default_cache_invalidation_time=None):
        """Create a BibolamaziFile object.

        If `fname` is provided, the file is fully loaded (unless `create` is also
        provided).

        If `create` is given and set to `True`, then an empty template is loaded and the
        internal file name is set to `fname`. The internal state will be set to ``LOADED''
        and calling `saveToFile()` will result in writing this template to the file
        `fname`.

        If `load_to_state` is given, then the file is only loaded up to the given state. 
        See `load()` for more details. The state should be one of `BIBOLAMAZIFILE_INIT`,
        `BIBOLAMAZIFILE_READ`, `BIBOLAMAZIFILE_PARSED` or `BIBOLAMAZIFILE_LOADED`.

        If `use_cache` is `True` (default), then when loading this file, we'll attempt to
        load a corresponding cache file if it exists. Note that even if `use_cache` is
        `False`, then cache will still be *written* when calling `saveToFile()`.

        If `default_cache_invalidation_time` is given, then the default cache invalidation
        time is set before loading the cache.
        """
        
        logger.debug("Opening bibolamazi file `%s'" %(fname));
        self._fname = None
        self._dir = None
        self._use_cache = use_cache

        if (create):
            self._init_empty_template();
            self._fname = fname
            self._dir = os.path.dirname(os.path.realpath(fname));
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

    def getLoadState(self):
        return self._load_state;

    def reset(self):
        self.load(fname=None, to_state=BIBOLAMAZIFILE_INIT)

    def load(self, fname=[], to_state=BIBOLAMAZIFILE_LOADED):
        """Loads the given file.

        If `fname` is `None`, then resets the object to an empty state. If fname is not given or an
        empty list, then uses any previously loaded fname and its state.

        If `to_state` is given, will only attempt to load the file up to that state. This
        can be useful, e.g., in a config editor which needs to parse the sections of the
        file but does not need to worry about syntax errors. The state should be one of
        `BIBOLAMAZIFILE_INIT`, `BIBOLAMAZIFILE_READ`, `BIBOLAMAZIFILE_PARSED` or
        `BIBOLAMAZIFILE_LOADED`.
        """
        
        if (fname or not isinstance(fname, list)):
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
                    logger.longdebug("File "+repr(self._fname)+" opened.");
                    self._read_config_stream(f, self._fname);
            except IOError as e:
                raise BibolamaziError(u"Can't open file `%s': %s" %(self._fname, unicode(e)));

        if (to_state >= BIBOLAMAZIFILE_PARSED  and  self._load_state < BIBOLAMAZIFILE_PARSED):
            self._parse_config()

        if (to_state >= BIBOLAMAZIFILE_LOADED  and  self._load_state < BIBOLAMAZIFILE_LOADED):
            self._load_contents()

        return True


    def fname(self):
        return self._fname;

    def fdir(self):
        return self._dir;

    def rawHeader(self):
        return self._header;

    def rawConfig(self):
        return self._config;

    def configData(self):
        return self._config_data;

    def rawStartConfigDataLineNo(self):
        """Returns the line number on which the begin config tag `CONFIG_BEGIN_TAG` is located.
        Line numbers start at 1 at the top of the file like in any reasonable editor.
        """
        return self._startconfigdatalineno;

    def fileLineNo(self, configlineno):
        """Returns the line number in the file of the config line `configlineno`. The latter
        refers to the line number INSIDE the config section, where line number 1 is right after
        the begin config tag `CONFIG_BEGIN_TAG`.
        """
        
        return configlineno + self._startconfigdatalineno;

    def configLineNo(self, filelineno):
        """Returns the line number in the config data corresponding to line `filelineno` in the
        file. Opposite of `fileLineNo()`.
        """
        
        return filelineno - self._startconfigdatalineno;

    def rawrest(self):
        return self._rest;

    def rawcmds(self):
        return self._cmds;

    def sources(self):
        return self._sources;

    def sourceLists(self):
        return self._source_lists;

    def filters(self):
        return self._filters;

    def bibliographyData(self):
        return self._bibliographydata;

    def bibliographydata(self):
        """
        .. deprecated 2.0:: use `bibliographyData()` instead!
        """
        butils.warn_deprecated("BibolamaziFile", "bibliographydata()", "bibliographyData()", __name__)
        return self.bibliographyData()

    def cacheFileName(self):
        """
        The file name where the cache will be stored. You don't need to access this
        directly, the cache will be loaded and saved automatically. You should normally
        only access the cache through cache accessors. See `cacheAccessor()`.
        """
        return self._fname + '.bibolamazicache';
        

    def cacheAccessor(self, klass):
        """
        Returns the cache accessor instance corresponding to the given class.
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
        # prefix every line by a percent sign.
        config_block = re.sub(r'^', '% ', configdata, flags=re.MULTILINE)

        # force ending in '\n' (but don't duplicate existing '\n')
        if (not len(config_block) or config_block[-1] != '\n'):
            config_block += '\n';

        # add start and end bibolamazi config section tags.
        config_block = CONFIG_BEGIN_TAG + '\n' + config_block + CONFIG_END_TAG + '\n'

        self.setRawConfig(config_block)


    def setRawConfig(self, configblock):
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

        This function expands '~/foo/bar' to e.g. '/home/someone/foo/bar', it expands
        shell variables, e.g. '$HOME/foo/bar' or '${MYBIBDIR}/foo/bar.bib'.

        If the path is relative, it is made absolute by interpreting it as relative to the
        location of this bibolamazi file (see `fdir()`).

        Note: `path` should not be an URL.
        """
        # expand ~/foo/bar, $HOME/foo/bar as well as ${MYBIBDIR}/foo/bar.bib
        path = os.path.expanduser(path);
        path = os.path.expandvars(path);
        # if the path is relative, make it absolute. I'ts relative to the bibolamazi file.
        # (note: `os.path.join(a, b)` will ignore `a` if `b` is absolute)
        return os.path.join(self._dir, path)


    def _init_empty_template(self):

        # provide us an initialized instance
        self.load(None, to_state=BIBOLAMAZIFILE_INIT)

        self._header = _TEMPLATE_HEADER;
        self._config = _TEMPLATE_CONFIG;
        self._config_data = self._config_data_from_block(_TEMPLATE_CONFIG);
        self._rest = '';#_TEMPLATE_REST;

        # store raw cmds
        self._cmds = [];

        # parse commands
        self._sources = [];
        self._source_lists = [];
        self._filters = [];
        self._cache_accessors = {};

        # cheat, we've loaded it manually
        self._load_state = BIBOLAMAZIFILE_LOADED

        self._bibliographydata = pybtex.database.BibliographyData();

        logger.longdebug('done with empty template init!');


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

        ST_HEADER = 0;
        ST_CONFIG = 1;
        ST_REST = 2;

        state = ST_HEADER;

        content = {
            ST_HEADER: u"",
            ST_CONFIG: u"",
            ST_REST: u""
            };
        config_block_lines = []

        lineno = 0;
        self._startconfigdatalineno = None;

        for line in stream:
            lineno += 1
            
            if (state == ST_HEADER and line.startswith(CONFIG_BEGIN_TAG)):
                state = ST_CONFIG;
                content[ST_CONFIG] += line;
                self._startconfigdatalineno = lineno;
                continue

            if (state == ST_CONFIG and line.startswith(CONFIG_END_TAG)):
                content[ST_CONFIG] += line;
                state = ST_REST;
                continue

            if (state == ST_CONFIG):
                # remove leading % signs
                #logger.debug("adding line to config_block: "+line);
                cline = line
                if (len(cline) and cline[-1] == '\n'):
                    cline = cline[:-1]
                config_block_lines.append(cline)

            content[state] += line;

        if (state != ST_REST):
            # file is not a bibolamazi file--no config section found.
            # error lineno is last line of file.
            raise NotBibolamaziFileError("Not a bibolamazi file--no config section found.",
                                         fname=self._fname, lineno=lineno)

        config_block = "\n".join(config_block_lines)

        # save the splitted data into these data structures.
        self._header = content[ST_HEADER];
        self._config = content[ST_CONFIG];
        self._config_data = self._config_data_from_input_lines(config_block);
        self._rest = content[ST_REST];

        logger.longdebug(("Parsed general bibolamazifile structure: len(header)=%d"+
                      "; len(config)=%d; len(config_data)=%d; len(rest)=%d") %
                     ( len(self._header),
                       len(self._config),
                       len(self._config_data),
                       len(self._rest) ) );


        logger.longdebug("config data is"+ "\n--------------------------------\n"
                     +self._config_data+"\n--------------------------------\n");

        self._load_state = BIBOLAMAZIFILE_READ
        return True

    def _parse_config(self):
        # now, parse the configuration.
        self._config_data = self._config_data_from_block(self._config);
        configstream = io.StringIO(unicode(self._config_data));
        cmds = [];
        emptycmd = BibolamaziFileCmd(cmd=None, text="", lineno=-1, linenoend=-1, info={})
        latestcmd = emptycmd;
        def complete_cmd():
            if (latestcmd.cmd is not None):
                cmds.append(latestcmd);

        thislineno = self._startconfigdatalineno
        for cline in configstream:
            thislineno += 1

            if (re.match(r'^\s*%%', cline)):
                # ignore comments
                continue
            
            if (re.match(r'^\s*$', cline)):
                # ignore empty lines
                # TODO: Maybe they shouldn't be ignored for filters? but then the cmd info stetches over
                # following comments etc. and in the GUI it behaves wierdly
                continue

            # try to match to a new command
            mcmd = re.match(r'^\s{0,1}(src|filter):\s*', cline);
            if (not mcmd):
                if (latestcmd.cmd is None):
                    # no command
                    self._raise_parse_error("Expected a bibolamazi command",
                                            lineno=thislineno);
                # simply continue current cmd
                latestcmd.text += cline;
                latestcmd.linenoend = thislineno;
                continue

            # we have completed the current cmd
            complete_cmd();
            latestcmd = emptycmd;
            # start new cmd
            cmd = mcmd.group(1);
            rest = cline[mcmd.end():];
            info = { };
            if (cmd == "filter"):
                # extract filter name
                mfiltername = re.match('^\s*(?P<filtername>(?:[\w.]+:)?\w+)(\s|$)', rest);
                if (not mfiltername):
                    self._raise_parse_error("Expected filter name", lineno=thislineno);
                filtername = mfiltername.group('filtername');
                rest = rest[mfiltername.end():];
                info['filtername'] = filtername;

            # and start cumulating stuff
            latestcmd = BibolamaziFileCmd(cmd=cmd, text=rest, lineno=thislineno, linenoend=thislineno, info=info);

        # complete the last cmd
        complete_cmd();

        # store raw cmds
        self._cmds = cmds;

        # parse commands
        self._sources = [];
        self._source_lists = [];
        self._filters = [];
        self._cache_accessors = {};
        for cmd in cmds:
            if (cmd.cmd == "src"):
                thesrc_list = shlex.split(cmd.text);
                self._source_lists.append(thesrc_list);
                self._sources.append(''); # this will be set later to which source in the
                #                           list was actually accessed.
                logger.debug("Added source list %r" % (thesrc_list));
                continue
            if (cmd.cmd == "filter"):
                filname = cmd.info['filtername'];
                filoptions = cmd.text;
                try:
                    filterinstance = factory.make_filter(filname, filoptions)
                    filterinstance.setBibolamaziFile(self)
                    filterinstance.setInvokationName(filname)
                    self._filters.append(filterinstance)
                except factory.NoSuchFilter as e:
                    self._raise_parse_error(str(e), lineno=cmd.lineno);
                except factory.NoSuchFilterPackage as e:
                    self._raise_parse_error(str(e), lineno=cmd.lineno);
                except factory.FilterError as e:
                    import traceback
                    logger.debug("FilterError:\n" + traceback.format_exc())
                    self._raise_parse_error(unicode(e),
                                            lineno=cmd.lineno);

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
                        
                logger.debug("Added filter '"+filname+"': `"+filoptions.strip()+"'");
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

        self._bibliographydata = None;

        if (not len(self._source_lists)):
            logger.warning("File `%s': No source files specified. You need source files to provide bib entries!"
                           %(self._fname));

        # now, populate all bibliographydata.
        for k in range(len(self._source_lists)):
            srclist = self._source_lists[k];
            src = self._populate_from_srclist(srclist);
            self._sources[k] = src;


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

        logger.longdebug('done with _load_contents!');
        return True


    def _populate_from_srclist(self, srclist):
        for src in srclist:
            # try to populate from this source
            ok = self._populate_from_src(src);
            if ok:
                return src
        logger.info("Ignoring nonexisting source list: %s" %(", ".join(srclist)));
        return None

    def _populate_from_src(self, src):
        bib_data = None;

        is_url = False
        if (re.match('^[A-Za-z0-9+_-]+://.*', src)):
            is_url = True
        
        if (not is_url):
            src = self.resolveSourcePath(src)

        # read data, decode it in the right charset
        data = None;
        if is_url:
            logger.debug("Opening URL %r", src);
            try:
                f = urllib.urlopen(src)
                if (f is None):
                    return None
                data = butils.guess_encoding_decode(f.read());
                logger.longdebug(" ... successfully read %d chars from URL resouce." % len(data));
                f.close();
            except IOError:
                # ignore source, will have to try next in list
                return None
        else:
            logger.debug("Opening file %r", src);
            try:
                with open(src, 'r') as f:
                    data = butils.guess_encoding_decode(f.read());
            except IOError:
                # ignore source, will have to try next in list
                return None;

        logger.info("Found Source: %s" %(src));

        # parse bibtex
        parser = inputbibtex.Parser();
        bib_data = None;
        with io.StringIO(data) as stream:
            bib_data = parser.parse_stream(stream);

        if (self._bibliographydata is None):
            # initialize bibliography data
            self._bibliographydata = pybtex.database.BibliographyData();

        for key, entry in bib_data.entries.iteritems():
            if (key in self._bibliographydata.entries):
                logger.warn('Repeated bibliography entry: %s. Keeping first encountered entry.', key)
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
            #    logger.warn('Repeated bibliography entry: %s. Renamed duplicate occurence to %s.', oldkey, key)

            self._bibliographydata.add_entry(key, entry)

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
        self._bibliographydata = bibliographydata;

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
        with codecs.open(self._fname, 'w', BIBOLAMAZI_FILE_ENCODING) as f:
            f.write(self._header);
            f.write(self._config);
            f.write(_repl(AFTER_CONFIG_TEXT, {
                r'__BIBOLAMAZI_VERSION__': butils.get_version(),
                r'__DATETIME_NOW__': datetime.now().isoformat()
                }));

            if (self._bibliographydata):
                w = outputbibtex.Writer();
                w.write_stream(self._bibliographydata, f);
            
            logger.info("Updated output file `"+self._fname+"'.");

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
% %% See comments below this configuration section if you're new to bibolamazi.
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

