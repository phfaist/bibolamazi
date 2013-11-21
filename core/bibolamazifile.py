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


import re;
import io;
import sys;
import os;
import os.path;
import codecs;
import shlex;
import urllib;
import cPickle as pickle;
from datetime import datetime;

import pybtex.database;
import pybtex.database.input.bibtex as inputbibtex;
import pybtex.database.output.bibtex as outputbibtex;

from core.blogger import logger;

from core import butils;
import filters;


class BibolamaziFileParseError(butils.BibolamaziError):
    def __init__(self, msg, fname=None, lineno=None):
        where = None
        if (fname is not None):
            where = fname
            if (lineno is not None):
                where += ", line %d" %(lineno)
                
        butils.BibolamaziError.__init__(self, msg, where=where);


def _repl(s, dic):
    for (k,v) in dic.iteritems():
        s = re.sub(k, v, s);
    return s;



def _to_bibusercacheobj(obj):
    if (isinstance(obj, BibUserCacheDic) or isinstance(obj, BibUserCacheList)):
        # make sure we don't make copies of these objects, but keep references
        # to the original instance. Especially important for the on_set_bind_to
        # feature.
        return obj
    if (isinstance(obj, dict)):
        return BibUserCacheDic(obj)
    if (isinstance(obj, list)):
        return BibUserCacheList(obj)
    return obj


class BibUserCacheDic(dict):
    def __init__(self, *args, **kwargs):
        self._on_set_bind_to = kwargs.pop('on_set_bind_to', None);
        
        super(BibUserCacheDic, self).__init__(*args, **kwargs)
        
    def __getitem__(self, key):
        return self.get(key, BibUserCacheDic({}, on_set_bind_to=(self, key)))

    def __setitem__(self, key, val):
        super(BibUserCacheDic, self).__setitem__(key, _to_bibusercacheobj(val))
        self._do_pending_bind()

    def setdefault(self, key, val):
        super(BibUserCacheDic, self).setdefault(key, _to_bibusercacheobj(val))
        self._do_pending_bind()

    def update(self, *args, **kwargs):
        # Problem: we need to make sure each value is filtered with _to_bibusercacheobj(val)
        raise NotImplementedError("Can't use update() with BibUserCacheDic: not implemented")
        #super(BibUserCacheDic, self).update(*args, **kwargs)
        #self._do_pending_bind()

    def _do_pending_bind(self):
        if (hasattr(self, '_on_set_bind_to') and self._on_set_bind_to is not None):
            (obj, key) = self._on_set_bind_to
            obj[key] = self
            self._on_set_bind_to = None

    def __repr__(self):
        return 'BibUserCacheDic(%s)' %(super(BibUserCacheDic, self).__repr__())


class BibUserCacheList(list):
    def __init__(self, *args, **kwargs):
        super(BibUserCacheList, self).__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        super(BibUserCacheList, self).__setitem__(key, _to_bibusercacheobj(val))
    
    def __repr__(self):
        return 'BibUserCacheList(%s)' %(super(BibUserCacheList, self).__repr__())


class BibUserCache(object):
    def __init__(self):
        self.cachedic = BibUserCacheDic({})

    def cache_for(self, cachename):
        if (self.cachedic is None):
            return None

        return self.cachedic[cachename]

    def has_cache(self):
        return bool(self.cachedic)

    def load_cache(self, cachefobj):
        self.cachedic = pickle.load(cachefobj);

    def save_cache(self, cachefobj):
        pickle.dump(self.cachedic, cachefobj, protocol=2);



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




class BibolamaziFile(object):
    def __init__(self, fname=None, create=False):
        """Create a BibolamaziFile object. If `fname` is provided, the file is fully loaded. If
        `create` is given and set to `True`, then an empty template is loaded and the internal
        file name is set to `fname`.
        """
        
        logger.debug("Opening bibolamazi file `%s'" %(fname));
        self._fname = None
        self._dir = None

        if (create):
            self._init_empty_template();
            self._fname = fname
            self._dir = os.path.dirname(os.path.realpath(fname));
        elif (fname):
            self.load(fname=fname, to_state=BIBOLAMAZIFILE_LOADED)
        else:
            logger.debug("No file given. Don't forget to set one with load()")

    def loadstate(self):
        return self._load_state;

    def reset(self):
        self.load(fname=None, to_state=BIBOLAMAZIFILE_INIT)

    def load(self, fname=[], to_state=BIBOLAMAZIFILE_LOADED):
        """Loads the given file.

        If `fname` is `None`, then resets the object to an empty state. If fname is not given or an
        empty list, then uses any previously loaded fname and its state.

        If `to_state` is given, will only attempt to load the file up to that state. This can be
        useful, e.g., in a config editor which needs to parse the sections of the file but does not
        need to worry about syntax errors.
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
            self._source_lists = None
            self._filters = None
            self._bibliographydata = None
            self._user_cache = BibUserCache()
            
        if (to_state >= BIBOLAMAZIFILE_READ  and  self._load_state < BIBOLAMAZIFILE_READ):
            try:
                with codecs.open(self._fname, 'r', encoding=BIBOLAMAZI_FILE_ENCODING) as f:
                    logger.longdebug("File "+repr(self._fname)+" opened.");
                    self._read_config_stream(f, self._fname);
            except IOError as e:
                raise butils.BibolamaziError(u"Can't open file `%s': %s" %(self._fname, unicode(e)));

        if (to_state >= BIBOLAMAZIFILE_PARSED  and  self._load_state < BIBOLAMAZIFILE_PARSED):
            self._parse_config()

        if (to_state >= BIBOLAMAZIFILE_LOADED  and  self._load_state < BIBOLAMAZIFILE_LOADED):
            self._load_contents()

            # then, try to load the cache if possible
            cachefname = self.cachefname()
            try:
                with open(cachefname, 'rb') as f:
                    logger.longdebug("Reading cache file %s" %(cachefname))
                    self._user_cache.load_cache(f)
            except (IOError, EOFError,):
                logger.debug("Cache file `%s' nonexisting or not readable." %(cachefname))
                pass

        return True


    def fname(self):
        return self._fname;

    def fdir(self):
        return self._dir;

    def rawheader(self):
        return self._header;

    def rawconfig(self):
        return self._config;

    def config_data(self):
        return self._config_data;

    def rawstartconfigdatalineno(self):
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

    def source_lists(self):
        return self._source_lists;

    def filters(self):
        return self._filters;

    def bibliographydata(self):
        return self._bibliographydata;

    def cachefname(self):
        """The file name where the cache will be stored. You don't need to access this directly,
        the cache will be loaded and saved automatically. You should normally only use the
        function `cache_for()`.
        """
        return self._fname + '.bibolamazicache';

    def cache_for(self, namespace):
        return self._user_cache.cache_for(namespace)

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


    def _init_empty_template(self):

        # provide us an initialized instance
        self.load(None, to_state=BIBOLAMAZIFILE_INIT)

        self._header = TEMPLATE_HEADER;
        self._config = TEMPLATE_CONFIG;
        self._config_data = self._config_data_from_block(TEMPLATE_CONFIG);
        self._rest = '';#TEMPLATE_REST;

        # store raw cmds
        self._cmds = [];

        # parse commands
        self._sources = [];
        self._source_lists = [];
        self._filters = [];

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
                mfiltername = re.match('^\s*(\w+)(\s|$)', rest);
                if (not mfiltername):
                    self._raise_parse_error("Expected filter name", lineno=thislineno);
                filtername = mfiltername.group(1);
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
                    filterinstance = filters.make_filter(filname, filoptions)
                    filterinstance.setBibolamaziFile(self)
                    self._filters.append(filterinstance)
                except filters.NoSuchFilter:
                    self._raise_parse_error("No such filter: `%s'" %(filname),
                                            lineno=cmd.lineno);
                except filters.FilterError as e:
                    import traceback
                    logger.debug("FilterError:\n" + traceback.format_exc())
                    self._raise_parse_error(unicode(e),
                                            lineno=cmd.lineno);
                logger.debug("Added filter '"+filname+"': `"+filoptions.strip()+"'");
                continue

            self._raise_parse_error("Unknown command: `%s'" %(cmd.cmd),
                                    lineno=cmd.lineno)

        self._load_state = BIBOLAMAZIFILE_PARSED

        logger.longdebug("done with _parse_config()")
        return True


    def _load_contents(self):

        self._bibliographydata = None;

        if (not len(self._source_lists)):
            logger.warning("File `%s': No source files specified. You need source files to provide bib entries!"
                           %(self._fname));

        # now, populate all bibliographydata.
        for k in range(len(self._source_lists)):
            srclist = self._source_lists[k];
            src = self._populate_from_srclist(srclist);
            self._sources[k] = src;

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

    def resolveSourcePath(self, path):
        # expand ~/foo/bar, $HOME/foo/bar as well as ${MYBIBDIR}/foo/bar.bib
        path = os.path.expanduser(path);
        path = os.path.expandvars(path);
        # if the path is relative, make it absolute. I'ts relative to the bibolamazi file.
        # (note: `os.path.join(a, b)` will ignore `a` if `b` is absolute)
        return os.path.join(self._dir, path)


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
            self._bibliographydata.add_entry(key, entry)

        return True



    def setBibliographyData(self, bibliographydata):
        self._bibliographydata = bibliographydata;

    def setEntries(self, bibentries):
        self._bibliographydata = pybtex.database.BibliographyData();
        self._bibliographydata.add_entries(bibentries);



    def save_to_file(self):
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
        if (self._user_cache.has_cache()):
            cachefname = self.cachefname()
            try:
                with open(cachefname, 'wb') as f:
                    logger.longdebug("Writing our cache to file %s" %(cachefname))
                    self._user_cache.save_cache(f)
            except IOError as e:
                logger.debug("Couldn't save cache to file `%s'." %(cachefname))
                pass

        




TEMPLATE_HEADER = """\


.. Additionnal stuff here will not be managed by bibolamazi. It will also not be
.. overwritten. You can e.g. temporarily add additional references here if you
.. don't have bibolamazi installed.


"""

TEMPLATE_CONFIG = """\
%%%-BIB-OLA-MAZI-BEGIN-%%%
%
% %% BIBOLAMAZI configuration section.
% %% Additional two leading percent signs indicate comments in the configuration.
%
% %% **** SOURCES ****
%
% %% The _first_ accessible file in _each_ source list will be read and filtered.
%
% src:   <source file 1> [ <alternate source file 1> ... ]
% src:   <source file 2> [ ... ]
%
% %% Add additional sources here. Alternative files are useful, e.g., if the same
% %% file must be accessed with different paths on different machines.
%
% %% **** FILTERS ****
%
% %% Specify filters here. Specify as many filters as you want, each with a `filter:'
% %% directive. See also `bibolamazi --list-filters' and `bibolamazi --help <filter>'.
%
% filter: filter_name  <filter options>
%
% %% Example:
% filter: arxiv -sMode=strip -sUnpublishedMode=eprint
%
% %% Finally, if your file is in a VCS, sort all entries by citation key so that you don't
% %% get huge file differences for each commit each time bibolamazi is run:
% filter: orderentries
%
%%%-BIB-OLA-MAZI-END-%%%
"""
