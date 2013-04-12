
import re;
import io;
import sys;
import codecs;
import os;
import os.path;

import pybtex.database;
import pybtex.database.input.bibtex as inputbibtex;
import pybtex.database.output.bibtex as outputbibtex;

from core.blogger import logger;
import filters;


class BibFilterInfoParseError(Exception):
    pass


encoding = 'utf-8';


class BibFilterFile:
    def __init__(self, fname):
        self._fname = fname;
        self._dir = os.path.dirname(os.path.realpath(fname));
        with codecs.open(fname, 'r', encoding) as f:
            self._parse_stream(f);

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

    def filters(self):
        return self._filters;

    def bibentries(self):
        return self._bibentries;
    

    def _parse_stream(self, stream):

        ST_HEADER = 0;
        ST_CONFIG = 1;
        ST_REST = 2;

        state = ST_HEADER;

        content = {
            ST_HEADER: "",
            ST_CONFIG: "",
            ST_REST: ""
            };

        for line in stream:
            
            if (state == ST_HEADER and line.startswith("%%%-BIBFILTER-BEGIN-%%%")):
                state = ST_CONFIG;
                continue

            if (state == ST_CONFIG and line.startswith("%%%-BIBFILTER-END-%%%")):
                state = ST_REST;
                continue

            if (state == ST_CONFIG):
                # remove leading % signs
                line = re.sub(r'^%', '', line);

            content[state] += line;

        # save the splitted data into these data structures.
        self._header = content[ST_HEADER];
        self._config = content[ST_CONFIG];
        self._rest = content[ST_REST];

        # now, parse the configuration.
        configstream = io.StringIO(unicode(self._config));
        cmds = [];
        emptycmd = [None, "", {}];
        latestcmd = emptycmd;
        def complete_cmd():
            if (latestcmd[0] is not None):
                cmds.append(latestcmd);

        for cline in configstream:
            if ((latestcmd[0] != "filter") and re.match('^\s*$', cline)):
                # ignore empty lines except for adding to 'filter' commands.
                continue

            # try to match to a new command
            mcmd = re.match(r'^\s{0,1}(src|filter):\s*', cline);
            if (not mcmd):
                if (latestcmd[0] is None):
                    # no command
                    raise BibFilterInfoParseError("Expected a bibclean command: `"+cline+"'");
                # simply continue current cmd
                latestcmd[1] += cline;
                continue

            # we have completed the current cmd
            complete_cmd();
            latestcmd = emptycmd;
            # start new cmd
            cmd = mcmd.group(1);
            rest = cline[mcmd.end():];
            info = {};
            if (cmd == "filter"):
                # extract filter name
                mfiltername = re.match('^\s*(\w+)(\s|$)', rest);
                if (not mfiltername):
                    raise BibFilterInfoParseError("Expected filter name: `"+cline+"'");
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
        self._filters = [];
        for cmd in cmds:
            if (cmd[0] == "src"):
                self._sources.append(cmd[1].strip());
                continue
            if (cmd[0] == "filter"):
                self._filters.append(filters.make_filter(cmd[2]['filtername'], cmd[1]));
                continue

            raise BibFilterInfoParseError("Unknown command: "+repr(cmd)+"");


        self._bibentries = None;

        # now, populate all bibentries.
        for src in self._sources:
            self._populate_from_src(src);

        logger.debug('done with init!');


    def _populate_from_src(self, src):
        bib_data = None;
        if (not os.path.isabs(src)):
            src = os.path.join(self._dir, src);
        try:
            with codecs.open(src, 'r', encoding) as f:
                parser = inputbibtex.Parser();
                bib_data = parser.parse_stream(f);
        except IOError:
            logger.info("Ignoring inexistant file "+src);
            # ignore file
            return None;

        if (self._bibentries is None):
            # initialize bibliography data
            self._bibentries = pybtex.database.BibliographyData();

        self._bibentries.add_entries(bib_data.entries.iteritems());




    def setentries(self, entries):
        self._bibentries = pybtex.database.BibliographyData();
        self._bibentries.add_entries(entries.iteritems());




    def save_to_file(self):
        with codecs.open(self._fname, 'w', encoding) as f:
            f.write(self._header);
            f.write('%%%-BIBFILTER-BEGIN-%%%\n');
            for line in io.StringIO(unicode(self._config)):
                f.write('%'+line);
            f.write('%%%-BIBFILTER-END-%%%\n');
            f.write('\n\n\n\n');

            w = outputbibtex.Writer();
            w.write_stream(self._bibentries, f);
        
        
        
