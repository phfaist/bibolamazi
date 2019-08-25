# -*- coding: utf-8 -*-
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

"""
This module defines callbacks and actions for parsing the command-line
arguments for bibolamazi. You're most probably not interested in this API. (Not
mentioning that it might change if I feel the need for it.)
"""

import re
import os
import sys
import os.path
import argparse
import logging

import bibolamazi.init
from .butils import getbool
from . import helppages

logger = logging.getLogger(__name__)

from .bibfilter.argtypes import LogLevel


class store_or_count(argparse.Action):
    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        # some checks
        if nargs != '?':
            raise ValueError('store_or_const: nargs must be "?"')

        if ('type' in kwargs):
            raise TypeError("Can't enforce a type on a store_or_count option!")
        
        super().__init__(option_strings, dest, nargs=nargs, const=None, **kwargs)


    def __call__(self, parser, namespace, values, option_string):
                
        try:
            val = getattr(namespace, self.dest)
        except AttributeError:
            val = 0

        # count -vv as -v -v
        if (isinstance(values, str) and not option_string.startswith('--') and len(option_string) > 1):
            optstr = option_string[1:]
            while values.startswith(optstr):
                # add an additional count for each additional specification of the option.
                val += 1
                values = values[len(optstr):] # strip that from the values
            if not values:
                values = None

        # Note: I don't know how to fix situations like "prog.py -v some_prog_arg" which is taken
        # as "-v some_prog_arg" ... we would need to interfere with the option parser to match the
        # argument not to the option (because of the wrong type), but to the program...


        # get the argument of -v (e.g.,  -v2  or  --verbose 2  or  --verbose=2 )
        if (isinstance(values, str)):
            try:
                values = int(values)
            except ValueError:
                opt_name = ", ".join(self.option_strings)
                parser.error(u"Invalid argument to %s: `%s' (maybe use %s option at the end of the command?)"
                             %(opt_name, values, opt_name))

        if (values is not None):
            # value provided
            val = int(values)
        else:
            val += 1
        
        setattr(namespace, self.dest, val)



rxkeyval = re.compile(r'^([\w.-]+)=(.*)$', re.DOTALL)

class store_key_val(argparse.Action):
    """
    Handles an ghostscript-style option of the type '-sBoolKey=some-value'.
    """
    def __init__(self, option_strings, dest, nargs=1, exception=ValueError, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_val actions must be == 1')

        self.exception = exception

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            **kwargs)


    def __call__(self, parser, namespace, values, option_string):
        # parse key-value pair in values
        if (isinstance(values, list)):
            values = values[0]
        m = rxkeyval.match(values)
        if not m:
            raise self.exception("cannot parse key=value pair: "+repr(values))

        keyvalpair = (m.group(1), m.group(2),)

        if (not self.dest):
            (key, val) = keyvalpair
            setattr(namespace, key, val)
        else:
            try:
                d = getattr(namespace, self.dest)
            except AttributeError:
                pass
            if not d:
                d = []
            d.append(keyvalpair)
            setattr(namespace, self.dest, d)


class store_key_bool(argparse.Action):
    """
    Handles an ghostscript-style option of the type '-dBoolKey' or '-dBoolKey=0'.
    """
    def __init__(self, option_strings, dest, nargs=1, const=True,
                 exception=ValueError, **kwargs):
        
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_bool actions must be == 1')

        self.exception = exception

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=bool(const),
            **kwargs)


    def __call__(self, parser, namespace, values, option_string):

        key = values[0]

        storeval = self.const

        eqindex = key.find('=')
        if (eqindex != -1):
            try:
                storeval = getbool(key[eqindex+1:])
                key = key[:eqindex]
            except ValueError as e:
                exc = self.exception(str(e))
                exc.opt_dest = self.dest
                raise exc

        if (not self.dest):
            setattr(namespace, key, self.const)
        else:
            try:
                d = getattr(namespace, self.dest)
                if d is None:
                    d = []
            except AttributeError:
                d = []
            d.append(
                (key, storeval,)
                )
            setattr(namespace, self.dest, d)




class store_key_const(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, const=True, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_const actions must be == 1')

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            **kwargs)


    def __call__(self, parser, namespace, values, option_string):

        key = values[0]

        if (not self.dest):
            setattr(namespace, key, self.const)
        else:
            try:
                d = getattr(namespace, self.dest)
                if d is None:
                    d = []
            except AttributeError:
                d = []
            d.append(key)
            setattr(namespace, self.dest, d)



class opt_action_help(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        if not values or values == "elp": # in case of -help: seen as -h elp
            helppages.cmdl_show_help('/general/cmdline', parser=parser)
            parser.exit()

        if values and len(values) and values[0] == '/':
            path = values
            helppages.cmdl_show_help(path, parser=parser)
            parser.exit()

        thefilter = values
        helppages.cmdl_show_help('/filter/'+thefilter, parser=parser)
        parser.exit()

class opt_action_helpwelcome(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        helppages.cmdl_show_help('/general/welcome', parser=parser)
        parser.exit()


class opt_action_version(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        p = helppages.get_help_page('/general/cmdlversion')
        sys.stdout.write(p.contentAsTxt())
        parser.exit()



class opt_list_filters(argparse.Action):
    def __init__(self, nargs=0, **kwargs):
        if nargs != 0:
            raise ValueError('nargs for opt_list_filters must be == 0')
        super().__init__(nargs=0, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string):
        helppages.cmdl_show_help('/filters')
        parser.exit()




class opt_init_empty_template(argparse.Action):
    def __init__(self, nargs=1, **kwargs):
        if nargs != 1:
            raise ValueError('nargs for init_empty_template must be == 1')
        
        argparse.Action.__init__(self, nargs=1, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string):

        from . import bibolamazifile

        try:
            newfilename = values[0]
        except IndexError:
            newfilename = values

        if (os.path.exists(newfilename)):
            logger.error("Cowardly refusing to overwrite existing file `%s'. Remove it first."
                         %(newfilename))
            parser.exit(9)

        bfile = bibolamazifile.BibolamaziFile(newfilename, create=True)
        bfile.saveToFile()

        parser.exit()




class opt_action_github_auth(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        ga = GithubAuthSetup(parser)

        if values:

            ga.setup_from_arg(values[0].strip())

        else:

            ga.interactive_enter()


class GithubAuthSetup:
    def __init__(self, parser):

        self.parser = parser

        from . import main
        self.main = main

    def setup_from_arg(self, arg):
        #
        # auth key directly specified as an option argument
        #
        if arg == '-':
            # unset auth
            self.unset_token_and_exit()
        elif arg == '?' or not arg:
            # empty argument, or '?' -- just run the interactive setup
            self.interactive_enter()
        else:
            self.save_token_and_exit(token)

            
    def print_status(self):
        status = self.main.get_github_auth_status()
        if status is None:
            print("Github authentication has not yet been configured.")
        elif status:
            print("Github authentication token is set.")
        else:
            print("Github authentication token is NOT set.")

        return status

    def interactive_enter(self):
        #
        # First of all, print the current config status
        #

        print("") # empty line
        status = self.print_status()

        if status: # token already configured

            # enter "manage token" menu
            self.interactive_manage_token()

        else:

            # directly ask to set a token
            self.interactive_setup_token()
            

    def interactive_manage_token(self):

        print("")
        print("""\
Would you like to:
    (1) unset the existing token,
    (2) set a new token, or
    (q) cancel and exit?
""")

        while True:
            action = input("Selection (1 or 2 or q): ").strip()
            if action in ['1', '2', 'q']:
                break
            print("""Invalid input, please type "1", "2", or "q".""")

        if action == '1':
            self.unset_token_and_exit()

        elif action == '2':
            self.interactive_setup_token()

        elif action == 'q':
            self.parser.exit(0)

        else:
            raise RuntimeError("It's not possible to get here")


    def interactive_setup_token(self):
        
        print("""\

INSTRUCTIONS FOR GITHUB AUTHENTICATION

This process will generate a personal access token authorizing bibolamazi to
access your github account. This procedure ensures that bibolamazi never sees
your github password. The personal access token can be revoked in your github
settings at any time.

Please visit this URL in your browser and follow the instructions below:

    https://github.com/settings/tokens

1. Click on the button “Generate new token”

2. Give a name to the access token such as “bibolamazi access”, and select the
   “repo” scope

3. Scroll down and click on “Generate token”

4. Paste the access token below:

""")

        token = input("Access token: ").strip()

        self.save_token_and_exit(token)



    def save_token_and_exit(self, token):

        # set the given token
        try:

            self.main.save_github_auth_token(token)

        except ValueError as e:

            logger.error(str(e))
            self.parser.exit(13)

        self.parser.exit()
        
    def unset_token_and_exit(self):

        # set the given token
        self.save_token_and_exit(None)
        





# Set up the logger according to the user's wishes
# ------------------------------------------------

class opt_set_verbosity(argparse.Action):
    def __init__(self, nargs=1, **kwargs):
        if nargs != 0 and nargs != 1:
            raise ValueError('nargs for opt_set_verbosity must be 0 or 1')
        
        argparse.Action.__init__(self, nargs=nargs, type=int, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string):

        from . import main

        if self.nargs == 1:
            verbositylevel = int(values[0])
        else:
            verbositylevel = self.const

        # act on the root logger
        loglevel = main.verbosity_logger_level(verbositylevel)
        rootlogger = logging.getLogger()
        rootlogger.setLevel(loglevel)

        logger.longdebug('Set verbosity: %d', verbositylevel)

        # finally, see if we should display information about where messages originated
        # from. Do this if the user specified a log level of severity less or equal to
        # DEBUG.
        if loglevel <= logging.DEBUG and hasattr(rootlogger, 'bibolamazi_formatter'):
            # show log-record-position-info (`[module lineno]: function():') for all messages
            rootlogger.bibolamazi_formatter.setShowPosInfoLevel(logging.CRITICAL)
        

# ------------------


class opt_set_fine_log_levels(argparse.Action):
    def __init__(self, nargs=1, **kwargs):
        if nargs != 1:
            raise ValueError('nargs for opt_set_fine_log_levels must be == 1')
        
        argparse.Action.__init__(self, nargs=nargs, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string):
        #
        # If there are some more fine-grained debug levels to set, go for it. Useful for
        # debugging bibolamazi components.
        #
        rootlogger = logging.getLogger()

        fine_log_levels = values[0]
        logger.longdebug("fine_log_levels=%r", fine_log_levels)

        lvlrx = re.compile(
            r'^\s*((?P<modname>[A-Za-z0-9_.]+)=)?(?P<level>(LONG)?DEBUG|WARNING|INFO|ERROR|CRITICAL)\s*$'
            )
        has_set_fine_levels = False
        for lvl in fine_log_levels.split(','):
            m = lvlrx.match(lvl)
            if not m:
                logger.warning("Bad fine-grained log level setting: `%s'", lvl)
                continue
            modname = m.group('modname')
            getloggerargs = {}
            if modname:
                getloggerargs['name'] = modname
            thelogger = logging.getLogger(**getloggerargs)
            try:
                thelevel = LogLevel(m.group('level')).levelno
            except ValueError as e:
                logger.warning("Bad fine-grained log level setting: bad level `%s': %s", m.group('level'), e)
                continue
            #print("setting Logger: modname=%r, getloggerargs=%r, thelogger=%r; to level %d"%(
            #    modname, getloggerargs, thelogger, thelevel
            #))
            thelogger.setLevel(thelevel)
            has_set_fine_levels = True

        # finally, see if we should display information about where messages originated
        # from. Do this if the user specified a nontrivial value to this option.
        if has_set_fine_levels and hasattr(rootlogger, 'bibolamazi_formatter'):
            # show log-record-position-info (`[module lineno]: function():') for all messages
            rootlogger.bibolamazi_formatter.setShowPosInfoLevel(logging.CRITICAL)

        logger.longdebug('Set fine log levels done.')
