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



CONFIG_BEGIN_TAG = '%%%-BIB-OLA-MAZI-BEGIN-%%%';
CONFIG_END_TAG = '%%%-BIB-OLA-MAZI-END-%%%';

AFTER_CONFIG_TEXT = _repl("""\
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





""", {r'__BIBOLAMAZI_VERSION__': butils.get_version(),
      r'__DATETIME_NOW__': datetime.now().isoformat()
      });

                    
# this is fixed to utf-8. No alternatives, sorry.
BIBOLAMAZI_FILE_ENCODING = 'utf-8';


class BibolamaziFile:
    def __init__(self, fname, create=False):
        logger.longdebug("opening file "+repr(fname));
        self._fname = fname;
        self._dir = os.path.dirname(os.path.realpath(fname));

        if (create):
            self._init_empty_template();
        else:
            try:
                with codecs.open(fname, 'r', BIBOLAMAZI_FILE_ENCODING) as f:
                    logger.longdebug("File "+repr(fname)+" opened.");
                    self._parse_stream(f, fname);
            except IOError as e:
                raise butils.BibolamaziError(u"Can't open file `%s': %s" %(fname, unicode(e)));

    def fname(self):
        return self._fname;

    def fdir(self):
        return self._dir;

    def rawheader(self):
        return self._header;

    def rawconfig(self):
        return self._config;

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
    

    def _init_empty_template(self):

        self._header = TEMPLATE_HEADER;
        self._config = TEMPLATE_CONFIG;
        self._config_data = self._config_data_from_input(TEMPLATE_CONFIG);
        self._rest = '';#TEMPLATE_REST;

        # store raw cmds
        self._cmds = [];

        # parse commands
        self._sources = [];
        self._source_lists = [];
        self._filters = [];

        self._bibliographydata = pybtex.database.BibliographyData();

        logger.longdebug('done with empty template init!');


    def _config_data_from_input(self, inputconfigdata):
        """
        Simply strips initial %'s on each line of `inputconfigdata`.
        """
        
        inputconfigdatalines = inputconfigdata.split('\n');
        config_data = '';
        for line in inputconfigdatalines:
            config_data += re.sub(r'^%', '', line)+'\n';

        return config_data;

        
    def _parse_stream(self, stream, streamfname=None):

        ST_HEADER = 0;
        ST_CONFIG = 1;
        ST_REST = 2;

        state = ST_HEADER;

        content = {
            ST_HEADER: u"",
            ST_CONFIG: u"",
            ST_REST: u""
            };
        config_data = u"";

        lineno = 0;
        startconfigdatalineno = None;

        def raise_parse_error(msg, lineno):
            raise BibolamaziFileParseError(msg, fname=streamfname, lineno=lineno)

        for line in stream:
            lineno += 1
            
            if (state == ST_HEADER and line.startswith(CONFIG_BEGIN_TAG)):
                state = ST_CONFIG;
                content[ST_CONFIG] += line;
                startconfigdatalineno = lineno;
                continue

            if (state == ST_CONFIG and line.startswith(CONFIG_END_TAG)):
                content[ST_CONFIG] += line;
                state = ST_REST;
                continue

            if (state == ST_CONFIG):
                # remove leading % signs
                #logger.debug("adding line to config_data: "+line);
                config_data += line; #re.sub(r'^%', '', line);

            content[state] += line;

        # save the splitted data into these data structures.
        self._header = content[ST_HEADER];
        self._config = content[ST_CONFIG];
        self._config_data = self._config_data_from_input(config_data);
        self._rest = content[ST_REST];
        
        logger.longdebug(("Parsed general bibolamazifile structure: len(header)=%d"+
                      "; len(config)=%d; len(config_data)=%d; len(rest)=%d") %
                     ( len(self._header),
                       len(self._config),
                       len(self._config_data),
                       len(self._rest) ) );


        logger.longdebug("config block is"+ "\n--------------------------------\n"
                     +self._config_data+"\n--------------------------------\n");

        # now, parse the configuration.
        configstream = io.StringIO(unicode(self._config_data));
        cmds = [];
        emptycmd = [None, "", {}];
        latestcmd = emptycmd;
        def complete_cmd():
            if (latestcmd[0] is not None):
                cmds.append(latestcmd);

        configlineno = 0
        for cline in configstream:
            configlineno += 1
            
            thislineno = startconfigdatalineno + configlineno;

            if (re.match(r'^\s*%%', cline)):
                # ignore comments
                continue
            
            if ((latestcmd[0] != "filter") and re.match(r'^\s*$', cline)):
                # ignore empty lines except for adding to 'filter' commands.
                continue

            # try to match to a new command
            mcmd = re.match(r'^\s{0,1}(src|filter):\s*', cline);
            if (not mcmd):
                if (latestcmd[0] is None):
                    # no command
                    raise_parse_error("Expected a bibolamazi command",
                                      lineno=thislineno);
                # simply continue current cmd
                latestcmd[1] += cline;
                continue

            # we have completed the current cmd
            complete_cmd();
            latestcmd = emptycmd;
            # start new cmd
            cmd = mcmd.group(1);
            rest = cline[mcmd.end():];
            info = { 'lineno': thislineno };
            if (cmd == "filter"):
                # extract filter name
                mfiltername = re.match('^\s*(\w+)(\s|$)', rest);
                if (not mfiltername):
                    raise_parse_error("Expected filter name", lineno=thislineno);
                filtername = mfiltername.group(1);
                rest = rest[mfiltername.end():];
                info['filtername'] = filtername;

            # and start cumulating stuff
            latestcmd = [cmd, rest, info];

        # complete the last cmd
        complete_cmd();

        # store raw cmds
        self._cmds = cmds;

        # parse commands
        self._sources = [];
        self._source_lists = [];
        self._filters = [];
        for cmd in cmds:
            if (cmd[0] == "src"):
                thesrc_list = shlex.split(cmd[1]);
                self._source_lists.append(thesrc_list);
                self._sources.append(''); # this will be set later to which source in the
                #                           list was actually accessed.
                logger.debug("Added source list %r" % (thesrc_list));
                continue
            if (cmd[0] == "filter"):
                filname = cmd[2]['filtername'];
                filoptions = cmd[1];
                try:
                    self._filters.append(filters.make_filter(filname, filoptions));
                except filters.NoSuchFilter:
                    raise_parse_error("No such filter: `%s'" %(filname),
                                      lineno=cmd[2]['lineno']);
                except filters.FilterError as e:
                    raise_parse_error(unicode(e),
                                      lineno=cmd[2]['lineno']);
                logger.debug("Added filter '"+filname+"': `"+filoptions.strip()+"'");
                continue

            raise_parse_error("Unknown command: `%s'" %(cmd),
                              lineno=cmd[2]['lineno'])


        self._bibliographydata = None;

        if (not len(self._source_lists)):
            logger.warning("File `%s': No source files specified. You need source files to provide bib entries!"
                           %(self._fname));

        # now, populate all bibliographydata.
        for k in range(len(self._source_lists)):
            srclist = self._source_lists[k];
            src = self._populate_from_srclist(srclist);
            self._sources[k] = src;

        logger.longdebug('done with _parse_stream!');


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
        
        if (not is_url and not os.path.isabs(src)):
            src = os.path.join(self._dir, src);

        # read data, decode it in the right charset
        data = None;
        if is_url:
            logger.debug("Opening URL %r", src);
            f = urllib.urlopen(src);
            if (f is None):
                return None
            data = butils.guess_encoding_decode(f.read());
            logger.longdebug(" ... successfully read %d chars from URL resouce." % len(data));
            f.close();
        else:
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
            f.write(AFTER_CONFIG_TEXT);

            w = outputbibtex.Writer();
            w.write_stream(self._bibliographydata, f);
            
            logger.info("Updated output file `"+self._fname+"'");
        
        
        




TEMPLATE_HEADER = """\



.. add additionnal stuff here. this will not be overwritten by bibolamazi.



"""

TEMPLATE_CONFIG = """\
%%%-BIB-OLA-MAZI-BEGIN-%%%
%
% %% BIBOLAMAZI configuration section.
% %% Additional two leading percent signs indicate comments in the configuration.
%
% %% **** SOURCES ****
%
% src:   <source file 1> [ <alternate source file 1> ... ]
% src:   <source file 2> [ ... ]
% %% add additional sources here; nonexisting files are ignored.
%
% %% **** FILTERS ****
%
% %% Specify filters here. Specify as many filters as you want, each with a `filter:'
% %% directive. See also `bibolamazi --list-filters' and `bibolamazi --help <filter>'.
%
% filter:   <filter specification>
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


# NOTE: this is ignored, as BibolamaziFile will automatically add its own "rest" upon save_to_file()
##TEMPLATE_REST = _repl("""\
##%
##%
##% ALL CHANGES BEYOND THIS POINT WILL BE LOST NEXT TIME BIBOLAMAZI IS RUN.
##%


##%
##% This template file was generated by BIBOLAMAZI __BIBOLAMAZI_VERSION__
##%
##%     https://github.com/phfaist/bibolamazi
##%
##% Bibolamazi collects bib entries from the sources listed in the configuration section
##% above, and merges them all into this file while applying the defined filters with
##% the given options. Your sources will not be altered.
##%
##% Any entries ABOVE the configuration section will be preserved as is, which means that
##% if you don't want to install bibolamazi or if it not installed, and you want to add
##% a bibliographic entry to this file, add it AT THE TOP OF THIS FILE.
##%
##%


##""", {r'__BIBOLAMAZI_VERSION__': butils.get_version(),
##      });