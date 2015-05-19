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
This module provides a collection of useful token checkers that can be used to make sure
the cache information is always valid and up-to-date.

Recall the Bibolamazi Cache is organized as nested dictionaries in which the cached
information is organized.

One main concern of the caching mechanism is that information be *invalidated* when it is
no longer relevant (between different runs of bibolamazi). This may be for example because
the original bibtex entry from the source has changed.

Each cache dictionary (:py:class:`BibUserCacheDic`) may be set a *token validator*, that
is a verifier instance class which will invalidate items it detects as no longer
valid. The validity of items is determined on the basis of *validation tokens*.

When an item in a cache dictionary is added or updated, a token (which can be any python
value) is generated corresponding to the cached value. This token may be, for example, the
date and time at which the value was cached. The validator then checks the tokens of the
cache values and detects those entries whose token indicates that the entries are no
longer valid: for example, if the token corresponds to the date and time at which the
entry was stored, the validator may invalidate all entries whose token indicates that they
are too old.

Token Checkers are free to decide what information to store in the tokens. See the
:py:mod:`tokencheckers` module for examples. Token checkers must derive from the base
class :py:class:`~tokencheckers.TokenChecker`.

"""


import datetime
import hashlib
import logging

import bibolamazi.init
from pybtex.database import Entry, Person

logger = logging.getLogger(__name__)



class TokenChecker(object):
    """
    Base class for a token checker validator.

    The :py:meth:`new_token` function always returns `True` and :py:meth:`cmp_tokens` just
    compares tokens for equality with the ``==`` operator.

    Subclasses should reimplement :py:meth:`new_token` to return something useful. 
    Subclasses may either use the default implementation equality comparision for
    :py:meth:`cmp_tokens` or reimplement that function for custom token validation
    condition (e.g. as in :py:class:`TokenCheckerDate`).
    """
    def __init__(self, **kwargs):
        super(TokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        """
        Return a token which will serve to identify changes of the dictionary entry `(key,
        value)`. This token may be any Python picklable object. It can be anything that
        :py:meth:`cmp_tokens` will undertsand.

        The default implementation returns `True` all the time. Subclasses should
        reimplement to do something useful.
        """
        return True

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        """
        Checks to see if the dictionary entry `(key, value)` is still up-to-date and
        valid. The old token, returned by a previous call to :py:meth:`new_token`, is
        provided in the argument `oldtoken`.

        The default implementation calls :py:meth:`new_token` for the `(key, value)` pair
        and compares the new token with the old token `oldtoken` for equality with the
        ``==`` operator. Depending on your use case, this may be enough so you may not
        have to reimplement this function (as, for example, in
        :py:class:`EntryFieldsTokenChecker`).

        However, you may wish to reimplement this function if a different comparision
        method is required. For example, if the token is a date at which the information
        was retrieved, you might want to test how old the information is, and invalidate
        it only after it has passed a certain amount of time (as done in
        :py:class:`TokenCheckerDate`).

        It is advisable that code in this function should be protected against having the
        wrong type in `oldtoken` or being given `None`. Such cases might easily pop up say
        between Bibolamazi Versions, or if the cache was once not properly set up. In any
        case, it's safer to trap exceptions here and return `False` to avoid an exception
        propagating up and causing the whole cache load process to fail.

        Return `True` if the entry is still valid, or `False` if the entry is out of date
        and should be discarded.
        """
        # by default, compare for equality.
        try:
            newtoken = self.new_token(key=key, value=value, **kwargs)
            if newtoken == oldtoken:
                #logger.longdebug("Basic cmp_tokens: newtoken=%r, oldtoken=%r ---> OK", newtoken, oldtoken)
                return True
            #logger.longdebug("Basic cmp_tokens: newtoken=%r, oldtoken=%r ---> DIFFERENT", newtoken, oldtoken)
            return False
        except Exception as e:
            logger.debug("Got exception in TokenChecker.cmp_tokens: ignoring and invalidating: %s", e)
            return False


class TokenCheckerDate(TokenChecker):
    """
    A :py:class:`TokenChecker` implementation that remembers the date and time at which an
    entry was set, and invalidates the entry after an amount of time `time_valid` has
    passed.

    The amount of time the information remains valid is given in the `time_valid` argument
    of the constructor or is set with a call to :py:meth:`set_time_valid`. In either case,
    you should provide a python :py:class:`datetime.time_delta` object.
    """
    def __init__(self, time_valid=datetime.timedelta(days=5), **kwargs):
        super(TokenCheckerDate, self).__init__(**kwargs)
        self.time_valid = time_valid

    def set_time_valid(self, time_valid):
        self.time_valid = time_valid

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        now = datetime.datetime.now()
        #logger.longdebug("Comparing %r with %r; time_valid=%r", now, oldtoken, self.time_valid)
        if oldtoken is None:
            return False
        try:
            return ((now - oldtoken) < self.time_valid)
        except Exception as e:
            logger.debug("Got exception in TokenCheckerDate.cmp_tokens, probably not a datetime object: "
                         "ignoring and invalidating: %s", e)
            return False

    def new_token(self, **kwargs):
        return datetime.datetime.now()


class TokenCheckerCombine(TokenChecker):
    """
    A :py:class:`TokenChecker` implementation that combines several different token
    checkers. A cache entry is deemed valid only if it considered valid by all the
    installed token checkers.

    For example, you may want to both make sure the cache has the right version (with a
    :py:class:`VersionTokenChecker` and that it is up-to-date).
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor. Pass as arguments here instances of token checkers to check for,
        e.g.::

            chk = TokenCheckerCombine(
                VersionTokenChecker('2.0'),
                EntryFieldsTokenChecker(bibdata, ['title', 'journal'])
                )
            
        """
        super(TokenCheckerCombine, self).__init__(**kwargs)
        self.subcheckers = args

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        try:
            for k in range(len(self.subcheckers)):
                chk = self.subcheckers[k]
                #logger.longdebug("TokenCheckerCombine: cmp_tokens(): #%d: %r : key=%s value=... oldtoken=%r",
                #                 k, chk, key, oldtoken[k])
                if not chk.cmp_tokens(key=key, value=value, oldtoken=oldtoken[k], **kwargs):
                    return False
            return True
        except Exception as e:
            logger.debug("Got exception in TokenCheckerCombine.cmp_tokens: ignoring and invalidating: %s", e)
            return False

    def new_token(self, key, value, **kwargs):
        return  tuple( (chk.new_token(key=key, value=value, **kwargs) for chk in self.subcheckers) )


class TokenCheckerPerEntry(TokenChecker):
    """
    A :py:class:`TokenChecker` implementation that associates different `TokenChecker`'s
    for individual entries, set manually.

    By default, the items of the dictionary are always valid. When an entry-specific token
    checker is set with :py:meth:`add_entry_check`, that token checker is used for that
    entry only.
    """
    def __init__(self, checkers={}, **kwargs):
        super(TokenCheckerPerEntry, self).__init__(**kwargs)
        self.checkers = checkers

    def add_entry_check(self, key, checker):
        """
        Add an entry-specific checker.

        `key` is the entry key for which this token checker applies. `checker` is the
        token checker instance itself. It is possible to make several keys share the same
        token checker instance.

        Note that no explicit validation is performed. (This can't be done because we
        don't even have a pointer to the cache dict.) So you should call manually
        :py:meth:`BibUserCacheDict.validate_item`

        If a token checker was already set for this entry, it is replaced by the new one.
        """
        if not checker:
            raise ValueError("add_entry_check(): may not provide `None`")
        if key in self.checkers:
            if self.checkers[key] is checker:
                return # already set
            logger.warning("TokenCheckerPerEntry: Replacing checker for `%s'", key)
        self.checkers[key] = checker

    def has_entry_for(self, key):
        """
        Returns `True` if we have a token checker set for the given entry `key`.
        """
        return (key in self.checkers)

    def checker_for(self, key):
        """
        Returns the token instance that has been set for the entry `key`, or `None` if no
        token checker has been set for that entry.
        """
        return self.checkers.get(key, None)

    def remove_entry_check(self, key):
        """
        As the name suggests, remove the token checker associated with the given entry key
        `key`. If no token checker was previously set, then this function does nothing.
        """
        if not key in self.checkers:
            return
        del self.checkers[key]

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        try:
            if not key in self.checkers:
                return True # no validation if we have no checkers
            return self.checkers[key].cmp_tokens(key=key, value=value, oldtoken=oldtoken, **kwargs)
        except Exception as e:
            logger.debug("Got exception in TokenCheckerPerEntry.cmp_tokens: ignoring and invalidating: %s", e)
            return False

    def new_token(self, key, value, **kwargs):
        if not key in self.checkers:
            return True # no validation if we have no checkers
        return self.checkers[key].new_token(key=key, value=value, **kwargs)




class EntryFieldsTokenChecker(TokenChecker):
    """
    A :py:class:`TokenChecker` implementation that checks whether some fields of a
    bibliography entry have changed.

    This works by calculating a MD5 hash of the contents of the given fields.
    """
    def __init__(self, bibdata, fields=[], store_type=False, store_persons=[], **kwargs):
        """
        Constructs a token checker that will invalidate an entry if any of its fields
        given here have changed.

        `bibdata` is a reference to the bibolamazifile's bibliography data; this is the
        return value of :py:meth:`~core.bibolamazifile.BibolamaziFile.bibolamaziData`.

        `fields` is a list of bibtex fields which should be checked for changes. Note that
        the 'author' and 'editor' fields are treated specially, with the `store_persons`
        argument.

        If `store_type` is `True`, the entry is also invalidated if its type changes (for
        example, from '@unpublished' to '@article').

        `store_persons` is a list of person roles we should check for changes (see person
        roles in :py:class:`pybtex.database.Entry` : this is either 'author' or 'editor'). 
        Specify for example 'author' here instead of in the `fields` argument. This is
        because `pybtex` treats the 'author' and 'editor' fields specially.
        """
        self.bibdata = bibdata
        self.fields = fields
        self.store_type = store_type
        if (isinstance(store_persons, bool)):
            self.store_persons = Person.valid_roles
        else:
            self.store_persons = [x for x in store_persons]

        super(EntryFieldsTokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        entry = self.bibdata.entries.get(key,Entry('misc'))

        data = "\n\n".join( (entry.fields.get(fld, '').encode('utf-8')
                         for fld in self.fields) )
        if self.store_type:
            data += "\n\n" + entry.type.encode('utf-8')
        if self.store_persons:
            data += "".join([
                ("\n\n"+p+":"+";".join([unicode(pers) for pers in entry.persons.get(p, [])]))
                for p in self.store_persons ]).encode('utf-8')
        
        return hashlib.md5(data).digest()



class VersionTokenChecker(TokenChecker):
    """
    A :py:class:`TokenChecker` which checks entries with a given version number.

    This is useful if you might change the format in which you store entries in your
    cache: adding a version number will ensure that any old-formatted entries will be
    discarded.
    """
    def __init__(self, this_version, **kwargs):
        """
        Constructs a version validator token checker.

        `this_version` is the current version. Any entry that was not exactly marked with
        the version `this_version` will be deemed invalid.

        `this_version` may actually be any python object. Comparision is done with the
        equality operator ``==`` (actually using the original :py:class:`TokenChecker`
        implementation).
        """
        super(VersionTokenChecker, self).__init__(**kwargs)
        self.this_version = this_version

    def new_token(self, key, value, **kwargs):
        return self.this_version


