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

import inspect
import datetime

from core.blogger import logger
from core.butils import call_with_args


class TokenChecker(object):
    def __init__(self, **kwargs):
        super(TokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        return True

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        # by default, compare for equality.
        if self.new_token(key=key, value=value, **kwargs) == oldtoken:
            return True
        return False


class TokenCheckerDate(TokenChecker):
    def __init__(self, time_valid=datetime.timedelta(days=3), **kwargs):
        super(TokenCheckerDate, self).__init__(**kwargs)
        self.time_valid = time_valid

    def set_time_valid(self, time_valid):
        self.time_valid = time_valid

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        if oldtoken is None:
            return False
        return ((datetime.now() - oldtoken) < self.time_valid)

    def new_token(self, **kwargs):
        return datetime.now()


class TokenCheckerCombine(TokenChecker):
    def __init__(self, *args, **kwargs):
        super(TokenCheckerCombine, self).__init__(**kwargs)
        self.subcheckers = args

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        for k in range(len(self.subcheckers)):
            chk = self.subcheckers[k]
            if not chk.cmp_tokens(self, key=key, value=value, oldtoken=oldtoken[k], **kwargs):
                return False
        return True

    def new_token(self, key, value, **kwargs):
        return  tuple( (chk.new_token(key=key, value=value, **kwargs) for chk in self.subcheckers) )


class TokenCheckerPerEntry(TokenChecker):
    def __init__(self, checkers={}, **kwargs):
        super(TokenCheckerPerEntry, self).__init__(**kwargs)
        self.checkers = checkers

    def add_entry_check(self, key, checker):
        if not checker:
            raise ValueError("add_entry_check(): may not provide `None`")
        self.checkers[key] = checker

    def has_entry_for(self, key):
        return (key in self.checkers)

    def checker_for(self, key):
        return self.checkers.get(key, None)

    def remove_entry_check(self, key):
        if not key in self.checkers:
            return
        del self.checkers[key]

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        if not key in self.checkers:
            return True # no validation if we have no checkers
        return self.checkers[key].cmp_tokens(key=key, value=value, oldtoken=oldtoken, **kwargs)

    def new_token(self, key, value, **kwargs):
        if not key in self.checkers:
            return True # no validation if we have no checkers
        return self.checkers[key].new_token(key=key, value=value, **kwargs)



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
    """
    Implements a cache where information may be stored between different runs of
    bibolamazi, and between different filter runs.

    This is a dictionary of key=value pairs, and can be used like a regular python
    dictionary.

    This implements *cache validation*, i.e. making sure that the values stored in the
    cache are up-to-date. Each entry of the dictionary has a corresponding *token*,
    i.e. a value (of any python picklable type) which will identify whether the cache is
    invalid or not. For example, the value could be `datetime` corresponding to the time
    when the entry was created, and the rule for validating the cache might be to check
    that the entry is not more than e.g. 3 days old.
    """
    def __init__(self, *args, **kwargs):
        self._on_set_bind_to = kwargs.pop('on_set_bind_to', None)

        # by default, no validation.
        self.tokenchecker = None
        self.tokens = {}

        # ---
        
        super(BibUserCacheDic, self).__init__(*args, **kwargs)

    def set_validation(self, tokenchecker, validate=True):
        """
        Set a function that will calculate the `token' for a given entry, for cache
        validation. The function `fn` shall compute a value based on a key (and possibly
        cache value) of the cache, such that comparision with `fncmp` (by default
        equality) will tell us if the entry is out of date. *********TODO: BETTER DOC
        **************

        If `validate` is `True`, then we immediately validate the contents of the cache.
        """

        # store this token checker
        self.tokenchecker = tokenchecker

        if validate:
            self.validate()

    def validate(self):
        """
        Validate this whole dictionary, i.e. make sure that each entry is still valid.

        This calls `validate_item()` for each item in the dictionary.
        """
        for key in self:
            self.validate_item(key)

    def validate_item(self, key):
        """
        Validate an entry of the dictionary manually. Usually not needed.

        If the value is valid, and happens to be a BibUserCacheDic, then that dictionary
        is also validated.

        Returns `True` if have valid item, otherwise `False`.
        """
        if not key in self:
            # not valid anyway.
            return False
        
        if not self.tokenchecker:
            # no validation
            return True

        val = self[key]
        if self.tokenchecker.cmp_tokens(key=key, val=val,
                                        oldtoken=self.tokens.get(key,None)):
            if isinstance(val, BibUserCacheDic):
                val.validate()
                # still return True independently of what happens in val.validate(),
                # because this dictionary is still valid.
            return True
        # otherwise, invalidate the cache. Don't just set to None or {} or [] because we
        # don't know what type the value is. This way is safe, because if getitem is
        # called, automatically an empty dic will be created.
        del self[key]
        del self.tokens[key]
        return False

    def __getitem__(self, key):
        return self.get(key, BibUserCacheDic({}, on_set_bind_to=(self, key)))

    def __setitem__(self, key, val):
        super(BibUserCacheDic, self).__setitem__(key, _to_bibusercacheobj(val))
        self._do_pending_bind()
        # assume that we __setitem__ is called, the value is up-to-date, ie. update the
        # corresponding token.
        if self.tokenchecker:
            self.tokens[key] = self.tokenchecker.new_token(key=key, val=val)

    def setdefault(self, key, val):
        super(BibUserCacheDic, self).setdefault(key, _to_bibusercacheobj(val))
        self._do_pending_bind()

    def update(self, *args, **kwargs):
        # Problem: we need to make sure each value is filtered with _to_bibusercacheobj(val)
        # ###: Wait, doesn't dict.update() call __setitem__() for each item?
        # ### ###: From what I see on stackoverflow, doesn't seems so
        raise NotImplementedError("Can't use update() with BibUserCacheDic: not implemented")
        #super(BibUserCacheDic, self).update(*args, **kwargs)
        #self._do_pending_bind()


    .......... # TODO: BUG: if an entry gets updated, then the parent dictionary does not get
    # a chance to update its token for the dictionary!! The dictionary should hold a
    # pointer to its parent, and inform it....

    def _do_pending_bind(self):
        if (hasattr(self, '_on_set_bind_to') and self._on_set_bind_to is not None):
            (obj, key) = self._on_set_bind_to
            obj[key] = self
            self._on_set_bind_to = None

    def __repr__(self):
        return 'BibUserCacheDic(%s)' %(super(BibUserCacheDic, self).__repr__())

    def __setstate__(self, state):
        self.clear()
        if not 'cache' in state or 'tokens' in state:
            # invalid cache
            logger.debug("Ignoring invalid cache")
            return

        cache = state['cache']
        tokens = state['tokens']
        for k,v in cache.iteritems():
            self[k] = v
            self.tokens[k] = tokens.get(k,None)

    def __getstate__(self):
        state = {
            'cache': {},
            'tokens': {},
            }
        for k,v in self.iteritems():
            state['cache'][k] = v
            state['tokens'][k] = self.tokens.get(k, None)

        return state



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
        self.validation_checker = TokenCheckerPerEntry()
        self.cachedic.set_validation(self.validation_checker)
        # an instance of an expiry_checker that several entries might share in
        # self.validation_checker.
        self.expiry_checker = TokenCheckerDate()

    def set_default_invalidation_time(self, time_delta):
        """
        A timedelta object giving the amount of time for which data in cache is consdered
        valid (by default).
        """
        self.expiry_checker.set_time_valid(time_delta)


    def cache_for(self, cachename, dont_expire=False):
        if (self.cachedic is None):
            return None

        if not dont_expire:
            # normal thing, i.e. the cache expires after N days
            self.validation_checker.add_entry_check(cachename, self.expiry_checker)
        elif self.validation_checker.has_entry_for(cachename):
            # conflict: twice cache requested with conflicting values of dont_expire
            raise RuntimeError("Conflicting values of dont_expire given for cache `%s'"%(cachename))

        return self.cachedic[cachename]
    

    def has_cache(self):
        return bool(self.cachedic)

    def load_cache(self, cachefobj):
        self.cachedic = pickle.load(cachefobj);

    def save_cache(self, cachefobj):
        pickle.dump(self.cachedic, cachefobj, protocol=2);

