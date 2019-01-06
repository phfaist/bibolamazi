################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013-2019 by Philippe Faist                                  #
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

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr


import re
import logging

from pybtex.database import BibliographyData, Entry
from pybtex.utils import OrderedCaseInsensitiveDict
import pybtex.bibtex.utils

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.core import butils

logger = logging.getLogger(__name__)



# --------------------------------------------------



HELP_AUTHOR = """\
apply_patches filter by Philippe Faist, (C) 2018-2019, GPL 3+
"""

HELP_DESC = """\
Applies patches marked in the bibliography database as special entries named "xxx.PATCH"
"""

HELP_TEXT = r"""

Suppose that you keep your bibtex database synchronized with a bibliography
manager.  Suppose that for a single document, you need to tweak some specific
bibtex entries (e.g., maybe you need add annot={...} fields with some specific
annotations which you otherwise wouldn't want to have).  You can do that by
creating a bibtex file with entries of the form "xyz.PATCH".  This filter
recognizes entries of this form: It looks for a corresponding bibtex entry with
key "xyz", and applies a set of changes described by the "PATCH" entry.

You can also selectively apply different sets of patches, identified by a "patch
series".  See below.

EXAMPLE:

Suppose our database has following the entry:

    @article{Einstein1935_EPR,
    author = {Einstein, Albert and Podolsky, Boris and Rosen, Nathan},
    doi = {10.1103/PhysRev.47.777},
    journal = {Physical Review},
    month = {may},
    number = {10},
    pages = {777--780},
    title = {Can Quantum-Mechanical Description of Physical Reality
             Be Considered Complete?},
    volume = {47},
    year = {1935}
    }

Now suppose we also have an entry, perhaps in a different source bibtex file, as
follows:

    @article{Einstein1935_EPR.PATCH,  % patch the Einsten1935EPR entry
    !type = {misc}                    % change bibtex entry type
    -doi = {},                        % remove "doi" field
    month = {May},                    % set "month" (replace)
    +note = {this is a cool paper}    % set "note" (append)
    }

After running the `apply_patches' filter, the Einstein1935_EPR.PATCH entry is
removed from the database, and the original Einstein1935_EPR entry becomes

    @misc{Einstein1935_EPR,
    author = {Einstein, Albert and Podolsky, Boris and Rosen, Nathan},
    journal = {Physical Review},
    month = {May},
    number = {10},
    pages = {777--780},
    title = {Can Quantum-Mechanical Description of Physical Reality
             Be Considered Complete?},
    volume = {47},
    year = {1935},
    note = {this is a cool paper}
    }

Note that the type was changed to "misc", the doi field was removed, the month
was changed to the capitalized version, and the note field was added.

PATCH SYNTAX REFERENCE:

The PATCH entry is read and parsed as a normal entry, but is interpreted
specially by the `apply_patches` filter as instructions of changes to perform on
a corresponding original bibtex entry.

fieldname = {...}

    Set the value of the given field to the new value.  If the field is already
    set, replace its value by the new one.

-fieldname = {}

    Remove the field from the entry entirely. The braces should be empty.

+fieldname = {...}

    Add the given field value to the existing field value.  If the field doesn't
    exist previously, set the field to this value.  If it does exist, then
    append this value using the separator specified by -sAddValueSeparator (by
    default, a comma and a space).

!type = {<new bibtex entry type>}

    Replace the bibtex entry type by the given type.  This is a special
    instruction that acts on the bibtex type instead of any field in particular.

PATCH SERIES:

If you have several patches, you can control when each patch is applied by
assigning them to different "patch series".  An instance of the 'apply_patches'
filter acts only on a given patch series.  Patches are associated to a patch
series by a suffix in the key, i.e.:

    @article{Einstein1935_EPR.PATCH.SERIESA,
    ...
    }

Would be associated with patch series "SERIESA".  To apply all patches from
"SERIESA", use:

    filter: apply_patches -sPatchSeries=SERIESA

No patch series suffix (i.e., a key like "Einstein1935_EPR.PATCH") corresponds
to the default patch series "" (the empty string).

"""



# ------------------------------------------------

class ApplyPatchesFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self, patch_series="", add_value_separator=", ", discard=False, *args):
        r"""
        Arguments:
        
        - patch_series: The given patch series is applied, i.e., the patches are
          given as entries whose keys are of the form
          "<OriginalBibtexKey>.PATCH.<PatchSeriesName>".  If no patch series is
          specified, the patches are those entries with keys of the form
          "<OriginalBibtexKey>.PATCH".

        - add_value_separator: Separator to use when concatenating values.  This
          happens when the original entry already has a given field value, and a
          patch instruction of the form "+field = {...}" is specified.

        - discard(bool): If set to `True`, then we discard all entries of the
          given patch series instead of applying the patches.  The original
          entries are left unchanged, and the bibliography database is cleared
          of these patch entries.
        """
        super(ApplyPatchesFilter, self).__init__()

        self.patch_series = patch_series
        self.add_value_separator = add_value_separator
        self.discard = discard

        logger.debug("apply_patches filter constructor done.")


    def getRunningMessage(self):
        seriesmsg = ""
        if self.patch_series:
            seriesmsg = " (series {})".format(self.patch_series)
        actionmsg = "Applying"
        if self.discard:
            actionmsg = "Discarding"
        return "{} entry patches{}".format(actionmsg, seriesmsg)


    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE



    def filter_bibolamazifile(self, bibolamazifile):

        #
        # bibdata is a pybtex.database.BibliographyData object
        #
        bibdata = bibolamazifile.bibliographyData()

        suffix = ".PATCH"
        if self.patch_series:
            suffix += "." + self.patch_series

        lensuffix = len(suffix)

        #
        # Iterate the bibliography data.  If an entry is found that is called
        # "XXX.PATCH[.SERIESNAME]", then apply patch to original entry.
        #

        patch_entry_key_list = []

        for (key, entry) in iteritems(bibdata.entries):
            if key.endswith(suffix):
                origkey = key[:-lensuffix]
                if not origkey in bibdata.entries:
                    logger.warning("Can't apply patch %s, entry %s is nonexistent",
                                   key, origkey)
                    continue
                
                # Store the patch key into the list of keys that have been
                # processed.  They will be deleted from the bibliography.
                patch_entry_key_list.append(key)

                # check if we are discarding the patch, or applying it
                if self.discard:
                    # don't apply patch, only discard it
                    continue

                # apply patch to original entry
                origentry = bibdata.entries[origkey]
                self.apply_patch(entry, origentry)


        for key in patch_entry_key_list:
            del bibdata.entries[key]

        return

    def apply_patch(self, patchentry, origentry):

        rxfld = re.compile('^(?P<op>[!+-]?)(?P<fld>.*)$')

        for f, val in iteritems(patchentry.fields):
            m = rxfld.match(f)
            op = m.group('op')
            fld = m.group('fld')

            if op == '!':
                # only special fields.
                if fld == 'type': # change entry type
                    origentry.type = val
                else:
                    logger.warning("Invalid patch special instruction for %s: field \"%s\"",
                                   patchentry.key, f)
                continue
        
            if fld in ('author','editor'):
                # special treatment for fields dealing with people.
                if op == '-':
                    origentry.persons[fld][:] = []
                elif op == '+':
                    # first, parse our val as a list of persons.
                    valp = [Person(p) for p in pybtex.bibtex.utils.split_name_list(val)]
                    origentry.persons[fld] += valp
                # no need for "else:" here, since op is necessarily set: a
                # simple 'author' or 'editor' field does not appear in
                # patchentry.fields but in patchentry.persons.  This case is
                # treated separately below by iterating patchentry.persons.
                continue

            if op == '-':
                # delete field in original entry
                origentry.fields.pop(fld,'')
                continue
            if op == '+':
                # add to field in original entry
                if fld in origentry.fields:
                    origentry.fields[fld] += self.add_value_separator + val
                else:
                    origentry.fields[fld] = val
                continue
            # update field in original entry
            origentry.fields[f] = val

        for role in patchentry.persons:
            if len(patchentry.persons[role]):
                origentry.persons[role][:] = patchentry.persons[role]

        logger.debug("Successfully applied patch %s", patchentry.key)



def bibolamazi_filter_class():
    return ApplyPatchesFilter

