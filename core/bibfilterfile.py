
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


CONFIG_BEGIN_TAG = '%%%-BIB-OLA-MAZI-BEGIN-%%%';
CONFIG_END_TAG = '%%%-BIB-OLA-MAZI-END-%%%';


encoding = 'utf-8';


class BibFilterFile:
    def __init__(self, fname):
        logger.debug("opening file "+repr(fname));
        self._fname = fname;
        self._dir = os.path.dirname(os.path.realpath(fname));

        with codecs.open(fname, 'r', encoding) as f:
            logger.debug("File "+repr(fname)+" opened.");
            self._parse_stream(f);

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

    def filters(self):
        return self._filters;

    def bibliographydata(self):
        return self._bibliographydata;
    

    def _parse_stream(self, stream):

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

        for line in stream:
            
            if (state == ST_HEADER and line.startswith(CONFIG_BEGIN_TAG)):
                state = ST_CONFIG;
                content[ST_CONFIG] += line;
                continue

            if (state == ST_CONFIG and line.startswith(CONFIG_END_TAG)):
                content[ST_CONFIG] += line;
                state = ST_REST;
                continue

            if (state == ST_CONFIG):
                # remove leading % signs
                #logger.debug("adding line to config_data: "+line);
                config_data += re.sub(r'^%', '', line);

            content[state] += line;

        # save the splitted data into these data structures.
        self._header = content[ST_HEADER];
        self._config = content[ST_CONFIG];
        self._config_data = config_data;
        self._rest = content[ST_REST];
        
        logger.debug(("Parsed general bibfilterfile structure: len(header)=%d"+
                      "; len(config)=%d; len(config_data)=%d; len(rest)=%d") %
                     ( len(self._header),
                       len(self._config),
                       len(self._config_data),
                       len(self._rest) ) );


        logger.debug("config block is"+ "\n--------------------------------\n"
                     +self._config_data+"\n--------------------------------\n");

        # now, parse the configuration.
        configstream = io.StringIO(unicode(self._config_data));
        cmds = [];
        emptycmd = [None, "", {}];
        latestcmd = emptycmd;
        def complete_cmd():
            if (latestcmd[0] is not None):
                cmds.append(latestcmd);

        for cline in configstream:
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
                    raise BibFilterInfoParseError("Expected a bibolamazi command: `"+cline+"'");
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
                thesrc = cmd[1].strip();
                self._sources.append(thesrc);
                logger.debug("Added source `"+thesrc+"'");
                continue
            if (cmd[0] == "filter"):
                filname = cmd[2]['filtername'];
                filoptions = cmd[1];
                try:
                    self._filters.append(filters.make_filter(filname, filoptions));
                except filters.NoSuchFilter:
                    logger.critical("No such filter: `"+filname+"'! Stop.");
                    exit(255);
                logger.debug("Added filter '"+filname+"': `"+filoptions.strip()+"'");
                continue

            raise BibFilterInfoParseError("Unknown command: "+repr(cmd)+"");


        self._bibliographydata = None;

        # now, populate all bibliographydata.
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

        if (self._bibliographydata is None):
            # initialize bibliography data
            self._bibliographydata = pybtex.database.BibliographyData();

        self._bibliographydata.add_entries(bib_data.entries.iteritems());




    def setBibliographyData(self, bibliographydata):
        self._bibliographydata = bibliographydata;

    def setEntries(self, bibentries):
        self._bibliographydata = pybtex.database.BibliographyData();
        self._bibliographydata.add_entries(bibentries);



    def save_to_file(self):
        with codecs.open(self._fname, 'w', encoding) as f:
            f.write(self._header);
            f.write(self._config);
            f.write(u'\n\n'+
                    u'% THIS FILE WAS AUTOMATICALLY GENERATED BY bibolamazi WITH THE ABOVE CONFIGURATION.\n'+
                    u'% ALL CHANGES BEYOND THIS POINT WILL BE LOST.\n'+
                    u'\n\n\n\n'
                    );

            w = outputbibtex.Writer();
            w.write_stream(self._bibliographydata, f);
            
            logger.debug("Updated output file `"+self._fname+"'");
        
        
        
