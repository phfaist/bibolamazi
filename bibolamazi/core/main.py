# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2018 by Philippe Faist                                       #
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
This module contains the code that implements Bibolamazi's main functionality. It also
provides the basic tools for the command-line interface.
"""

import os
import os.path
import re
import sys
import argparse
import textwrap
from collections import namedtuple
import json
import logging

import appdirs

# import all the parts we need from our own application.
# ------------------------------------------------------

import bibolamazi.init
# rest of the modules
from . import blogger
from . import version
from .bibolamazifile import BibolamaziFile
from . import argparseactions
from . import butils
from .butils import BibolamaziError
from .bibfilter import factory as filterfactory
from .bibfilter import pkgprovider, pkgfetcher_github


# our logger for the main module
logger = logging.getLogger(__name__)


from .bibfilter.argtypes import LogLevel


# ------------------------------------------------------------------------------


# code to set up logging mechanism, if run by command-line

def verbosity_logger_level(verbosity):
    """
    Simple mapping of 'verbosity level' (used, for example for command line
    options) to correspondig logging level (:py:const:`logging.DEBUG`,
    :py:const:`logging.ERROR`, etc.).
    """
    if verbosity == 0:
        return logging.ERROR
    elif verbosity == 1:
        return logging.INFO
    elif verbosity == 2:
        return logging.DEBUG
    elif verbosity >= 3:
        return blogger.LONGDEBUG

    raise ValueError("Bad verbosity level: %r" %(verbosity))




# ------------------------------------------------------------------------------


class BibolamaziNoSourceEntriesError(BibolamaziError):
    def __init__(self):
        msg = "Error: No source entries found. Stopping before we overwrite the bibolamazi file."
        BibolamaziError.__init__(self, msg)



def setup_filterpackage_from_argstr(argstr):
    """
    Add a filter package definition and path to filterfactory.filterpath from a string
    that is a e.g. a command-line argument to --filterpackage or a part of the environment
    variable BIBOLAMAZI_FILTER_PATH.
    """

    (fpname, fpdir) = filterfactory.parse_filterpackage_argstr(argstr)

    try:
        ok = filterfactory.validate_filter_package(fpname, fpdir, raise_exception=True)
    except filterfactory.NoSuchFilterPackage as e:
        raise BibolamaziError(str(e))

    filterfactory.filterpath[fpname] = fpdir
    

def setup_filterpackages_from_env():
    if 'BIBOLAMAZI_FILTER_PATH' in os.environ:
        logger.debug("Detected BIBOLAMAZI_FILTER_PATH=%s, using it" %(os.environ['BIBOLAMAZI_FILTER_PATH']))
        for fp in reversed(os.environ['BIBOLAMAZI_FILTER_PATH'].split(os.pathsep)):
            setup_filterpackage_from_argstr(fp)

class AddFilterPackageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setup_filterpackage_from_argstr(values)
    

def get_args_parser():

    parser = argparse.ArgumentParser(
        description='Prepare consistent BibTeX files for your LaTeX documents',
        prog='bibolamazi',
        epilog="Log messages will be produced in color by default "
        "if outputting to a TTY. To override the use of TTY colors, "
        "set environment variable BIBOLAMAZI_TTY_COLORS to 'yes', 'no' "
        "or 'auto'.",
        add_help=False)

    group = parser.add_argument_group("Bibolamazi file")
    group.add_argument(
        '-o', '--output', action='store', dest='output', metavar="FILE", nargs='?',
        help="Do not overwrite the original bibolamazi file, and write "
        "instead bibolamazi output to FILE. (Note: the cache is still "
        "saved using the old file name with extension \".bibolamazicache\" "
        "for future use.)"
    )

    group.add_argument(
        '-N', '--new', action=argparseactions.opt_init_empty_template, nargs=1,
        metavar="NEW_FILENAME",
        help="Create a new bibolamazi file with a template configuration."
    )

    group = parser.add_argument_group("Cache control")
    group.add_argument(
        '-C', '--no-cache', action='store_false', dest='use_cache', default=True,
        help="Do not read any existing cache file and regenerate the cache. If "
        "the cache file exists, it will be overwritten."
    )
    group.add_argument(
        '-z', '--cache-timeout', dest='cache_timeout', type=butils.parse_timedelta,
        default=None,
        help="The default timeout after which to consider items in cache to be invalid. "
        "Not all cache items honor this. Format: '<N><unit>' with unit=w/d/m/s"
    )

    group = parser.add_argument_group("Filter packages")
    group.add_argument(
        '--filterpackage', action=AddFilterPackageAction,
        help="Add a package name in which to search for filters. You may specify this "
        "option multiple times; last specified filter packages are searched first. Valid "
        "values for this option are either (1) a simple python package name (if it is in the "
        "PYTHONPATH); (2) a string 'pkgname=/some/location' where pkgname is the python "
        "package name which will be loaded with the given path prepended to sys.path; or "
        "(3) a full path to a package directory '/some/location/to/pkgname' which has the "
        "same effect as the value 'pkgname=/some/location/to'."
    )

    group.add_argument(
        '--github-auth', action=argparseactions.opt_action_github_auth, nargs='?',
        help="Store authentication information for accessing filter packages specified "
        "directly as github repositories.  Use this option without argument for an "
        "interactive setup, or if you know what you're doing, directly specify the "
        "access token as argument to this option or specify '-' as argument to reset "
        "the stored authentication."
    )

    group = parser.add_argument_group("Logging verbosity")
    group.add_argument(
        '--verbosity', action=argparseactions.opt_set_verbosity, nargs=1,
        help="Set verbosity level (0=quiet, 1=info (default), 2=verbose, 3=long debug)."
    )
    group.add_argument(
        '-q', '-v0', '--quiet', action=argparseactions.opt_set_verbosity, nargs=0, const=0,
        help="Don't display any messages (same as --verbosity=0)"
    )
    group.add_argument(
        '-v1', action=argparseactions.opt_set_verbosity, nargs=0, const=1,
        help='Set normal verbosity mode (same as --verbosity=1)'
    )
    group.add_argument(
        '-v', '-v2', '--verbose', action=argparseactions.opt_set_verbosity, nargs=0, const=2,
        help='Set verbose mode (same as --verbosity=2)'
    )
    group.add_argument(
        '-vv', '-v3', '--long-verbose', action=argparseactions.opt_set_verbosity,
        nargs=0, const=3,
        help='Set very verbose mode, with long debug messages (same as --verbosity=3)'
    )
    group.add_argument(
        '--fine-log-levels', action=argparseactions.opt_set_fine_log_levels,
        help=textwrap.dedent('''\
        Fine-grained logger control: useful for debugging filters or
        bibolamazi itself. This is a comma-separated list of modules and
        corresponding log levels to set, e.g.
        "core=INFO,filters=DEBUG,filters.arxiv=LONGDEBUG", where if in an
        item no module is given (but just a level or number), then the
        root logger is addressed. Possible levels are (%s)
        ''')%(
            ", ".join( (x[0] for x in LogLevel.levelnos) )
        )
    )

    group = parser.add_argument_group("Help pages")
    group.add_argument(
        '--help', '-h', action=argparseactions.opt_action_help, nargs='?',
        metavar='filter',
        help='Show this help message and exit. If filter is given, show information and '
        'help text for that filter. See --list-filters for a list of available filters.'
    )
    group.add_argument(
        '--help-welcome', action=argparseactions.opt_action_helpwelcome, nargs=0,
        help='Show a brief introduction to bibolamazi and how to use it.'
    )
    group.add_argument(
        '-F', '--list-filters', action=argparseactions.opt_list_filters, dest='list_filters',
        help="Show a list of available filters along with their description, and exit."
    )
    group.add_argument(
        '--version', action=argparseactions.opt_action_version, nargs=0,
        help='Show bibolamazi version number and exit.'
    )

    parser.add_argument(
        'bibolamazifile',
        # note the %'s are parsed as formatting:
        help='The .bibolamazi.bib file to update, i.e. that contains the %%%%%%-BIB-OLA-MAZI '
        'configuration tags.'
    )

    return parser



ArgsStruct = namedtuple('ArgsStruct', ('bibolamazifile', 'use_cache', 'cache_timeout', 'output'))



def main(argv=sys.argv[1:]):

    try:

        # run main program
        _main_helper(argv)
        
    except SystemExit:
        raise
    
    except KeyboardInterrupt:
        raise

    except BibolamaziError as e:
        logger.error("\n" + str(e))

    except: # lgtm [py/catch-base-exception]
        
        print()
        print(" -- EXCEPTION --")
        print()

        # debugging post-mortem
        import traceback; traceback.print_exc()
        import pdb; pdb.post_mortem()


class CmdlSettings:
    """
    Stores settings for the command-line app.  Read/write json-objects to the
    `config` property of this object.  Config is loaded upon object
    creation. Call `saveConfig()` after changing the `config` property.
    """
    def __init__(self, configfname='cmdl_settings.json'):
        super().__init__()
        self.configfname = configfname

        self.user_config_dir = appdirs.user_config_dir('bibolamazi')
        if not os.path.exists(self.user_config_dir):
            os.makedirs(self.user_config_dir, exist_ok=True)
        self.full_config_fname = os.path.join(self.user_config_dir, self.configfname)

        self.config = {}

        self.reloadConfig()

        if 'RemoteFilterPackages' not in self.config:
            self.config['RemoteFilterPackages'] = {}
        
    def reloadConfig(self):
        if os.path.exists(self.full_config_fname):
            try:
                with open(self.full_config_fname) as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning("Failed to load config file %s: %s", self.full_config_fname, e)

    def saveConfig(self):
        with open(self.full_config_fname, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    
# Note: not used by GUI
class CmdlMainPackageProviderManager(pkgprovider.PackageProviderManager):
    def __init__(self):
        super().__init__()
        settings = CmdlSettings()
        self.prompted_for_remote = settings.config['RemoteFilterPackages'].get('PromptedForRemote', False)
        self.allow_remote = settings.config['RemoteFilterPackages'].get('AllowRemote', False)

    def remoteAllowed(self):
        if not self.prompted_for_remote:
            # ask for remote
            print("""\

WARNING: Filter packages are python scripts that can execute arbitrary code.
Only run filters from sources you trust.  Do you want to enable automatically
downloading remote packages when a remote package is specified?

""")

            yn = None
            while yn not in ['Y', 'n']:
                yn = input('Allow remote packages? (Y/n) ')
                yn = yn.strip()[0]
                if yn not in ['Y', 'n']:
                    print("Please answer with Y or n.")

            self.allow_remote = ( yn == 'Y' )

            self.prompted_for_remote = True
            settings = CmdlSettings()
            settings.config['RemoteFilterPackages']['PromptedForRemote'] = True
            settings.config['RemoteFilterPackages']['AllowRemote'] = self.allow_remote
            settings.saveConfig()

            if self.allow_remote:
                logger.warning("Allowing remote filter packages for future sessions. Edit "
                               "config file %s to change this.", settings.full_config_fname)
            

        elif not self.allow_remote:
            settings = CmdlSettings()
            logger.warning("Remote filter packages have been disabled. Edit config file %s"
                           " to change.", settings.full_config_fname)

        return self.allow_remote
            

# Note: gui doesn't use these, see bibolamazi_gui.bibolamaziapp
cmdl_filterpackage_providers = {}

def load_filterpackage_providers():
    settings = CmdlSettings()

    # first, create our package provider manager.
    filterfactory.package_provider_manager = CmdlMainPackageProviderManager()

    github_auth_token = settings.config['RemoteFilterPackages'].get('GithubAuthToken', '')
    if github_auth_token:
        github_auth_token = github_auth_token.strip()
    if not github_auth_token:
        github_auth_token = None

    cmdl_filterpackage_providers['github'] = \
        pkgfetcher_github.GithubPackageProvider(github_auth_token)

    filterfactory.package_provider_manager.registerPackageProvider(
        cmdl_filterpackage_providers['github']
    )

    #print("Loaded filterpackage providers (cmdl version)")

def get_github_auth_status():
    """
    Returns one of `None` (no configuration provided), `False` (configuration
    exists, token explicitly not set), and `True` (token previously set and
    saved).
    """

    settings = CmdlSettings()
    if 'RemoteFilterPackages' not in settings.config:
        return None
    if 'GithubAuthToken' not in settings.config['RemoteFilterPackages']:
        return None

    token = settings.config['RemoteFilterPackages']['GithubAuthToken']
    if token is not None and token.strip():
        return True

    return False

def _check_token_valid(token):
    if re.match(r'^[a-zA-Z0-9]{32,}$', token) is None:
        raise ValueError("Invalid access token provided")

def save_github_auth_token(github_auth_token):

    # no need to mess with objects in cmdl_filterpcakage_providers -- anyway
    # we'll quit right away after saving the token to the config file.
    #
    #cmdl_filterpackage_providers['github'].setAuthToken(github_auth_token)

    settings = CmdlSettings()
    if 'RemoteFilterPackages' not in settings.config:
        settings.config['RemoteFilterPackages'] = {}

    if github_auth_token is not None:
        _check_token_valid(github_auth_token) # raise ValueError for invalid token

    settings.config['RemoteFilterPackages']['GithubAuthToken'] = github_auth_token
    settings.saveConfig()

    logger.debug("Set auth token %s",
                 '[...]{}'.format(github_auth_token[-4:]) if github_auth_token else 'None')

    if github_auth_token is not None:
        logger.info("Github authentication token set.")
    else:
        logger.info("Unset github authentication token.")



def _main_helper(argv):

    # get some basic logging mechanism running
    blogger.setup_simple_console_logging()
    # start with level INFO
    logging.getLogger().setLevel(logging.INFO)

    # load precompiled filters, if we've got any
    # ------------------------------------------
    #try:
    #    import bibolamazi.bibolamazi_compiled_filter_list as pc
    #    filters_factory.load_precompiled_filters('bibolamazi.filters', dict([
    #        (fname, pc.__dict__[fname])  for fname in pc.filter_list
    #        ]))
    #except ImportError:
    #    pass


    # set up the filter package providers
    # -----------------------------------
    load_filterpackage_providers()
    
    # set up extra filter packages from environment variables
    # -------------------------------------------------------

    setup_filterpackages_from_env()

    
    # parse the command line arguments
    # --------------------------------

    parser = get_args_parser()

    args = parser.parse_args(args=argv)

    return run_bibolamazi_args(args)



def run_bibolamazi(bibolamazifile, **kwargs):
    # defaults
    kwargs2 = {
        'use_cache': True,
        'cache_timeout': None,
        'output': None
        }
    kwargs2.update(kwargs)
    args = ArgsStruct(bibolamazifile, **kwargs2)
    return run_bibolamazi_args(args)


def run_bibolamazi_args(args):
    #
    # args is supposed to be the parsed arguments from main()
    #

    logger.debug(textwrap.dedent("""
    Bibolamazi Version %(ver)s by Philippe Faist (C) %(copy_year)s

    Use option --help for help information.
    """         %   {
                     'ver': version.version_str,
                     'copy_year': version.copyright_year,
                     }))


    # open the bibolamazifile, which is the main bibtex file
    # ------------------------------------------------------

    kwargs = {
        'use_cache': args.use_cache
        }

    #
    # If given a cache_timeout, give it as parameter
    #
    if args.cache_timeout is not None:
        logger.debug("default cache timeout: %r", args.cache_timeout)
        kwargs['default_cache_invalidation_time'] = args.cache_timeout
    

    # open the bibolamazi file and create the BibolamaziFile object. This will parse the rules
    # and the entries, as well as keep some information on how to re-write to the file.
    bfile = BibolamaziFile(args.bibolamazifile, **kwargs)


    bibdata = bfile.bibliographyData()
    if (bibdata is None or not len(bibdata.entries)):
        logger.critical("No source entries found. Stopping before we overwrite the bibolamazi file.")
        raise BibolamaziNoSourceEntriesError()


    # now, run the selected filters in the corresponding order.
    # ---------------------------------------------------------

    for filtr in bfile.filters():
        #
        # For debugging: dump the library at each filter step on level longdebug()
        #
        if logger.isEnabledFor(blogger.LONGDEBUG):
            s = "========== Dumping Bibliography Database ==========\n"
            for key, entry in bibdata.entries.items():
                s += "  %10s: %r\n\n"%(key, entry)
            s += "===================================================\n"
            logger.longdebug(s)

        bfile.runFilter(filtr)


    # and output everything ...
    if args.output:
        # ...  to the specified file:
        bfile.saveToFile(fname=args.output)
    else:
        # ...  or back to the original file:
        bfile.saveToFile()


    logger.debug('Done.')

    return None



if __name__ == "__main__":
    
    main()
