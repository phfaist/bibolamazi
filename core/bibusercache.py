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


class validtoken_date:
    def __init__(time_valid=datetime.timedelta(days=3)):
        self.time_valid = time_valid

    def __call__(self, x, oldvalidtoken):
        if oldvalidtoken is None:
            return False
        return ((datetime.now() - oldvalidtoken) < self.time_valid)

    @staticmethod
    def newvalidtoken(x=None):
        return datetime.now()


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
    cache are up-to-date. Each entry of the dictionary has a corresponding *validtoken*,
    i.e. a value (of any python picklable type) which will identify whether the cache is
    invalid or not. For example, the value could be `datetime` corresponding to the time
    when the entry was created, and the rule for validating the cache might be to check
    that the entry is not more than e.g. 3 days old.
    """
    def __init__(self, *args, **kwargs):
        self._on_set_bind_to = kwargs.pop('on_set_bind_to', None)

        # by default, no validation.
        self.validtoken_fn = None
        self.validtoken_fncmp = None

        self.validtokens = {}

        # ---
        
        super(BibUserCacheDic, self).__init__(*args, **kwargs)

    def set_validation(self, fn, fncmp=None, validate=True):
        """
        Set a function that will calculate the `validtoken' for a given entry. The
        function `fn` shall compute a value based on a key (and possibly cache value) of
        the cache, such that comparision with `fncmp` (by default equality) will tell us
        if the entry is out of date. *********TODO: BETTER DOC **************

        If `validate` is `True`, then we immediately validate the contents of the cache.
        """

        # store this validtoken_fn
        self.validtoken_fn = fn

        # validtoken_fncmp:

        if not fncmp:
            # default comparator is equality: if two tokens are different then the cache
            # is invalid.
            validtoken_fncmp = (lambda key, val, oldvalidtoken, self=self:
                                (self.call_validtoken_fn(x, key=key) is oldvalidtoken)
                                )
        self.validtoken_fncmp = validtoken_fncmp

        if validate:
            self.validate()


    def call_validtoken_fn(self, key, val):
        if not self.validtoken_fn:
            return True
        return call_with_args(self.validtoken_fn, key=key, val=val)

    def call_validtoken_fncmp(self, key, val, oldvalidtoken):
        if not self.validtoken_fncmp:
            return True # always valid in case of no validation
        return call_with_args(self.validtoken_fncmp, key=key, val=val, oldvalidtoken=oldvalidtoken)
        
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
        
        val = self[key]
        if self.call_validtoken_fncmp(key=key, val=val,
                                      oldvalidtoken=self.validtokens.get(key,None)):
            if isinstance(val, BibUserCacheDic):
                val.validate()
                # still return True independently of val.validate(), because this
                # dictionary is still valid.
            return True
        # otherwise, invalidate the cache. Don't just set to None or {} or [] because we
        # don't know what type the value is. This way is safe, because if getitem is
        # called, automatically an empty dic will be created.
        del self[key]
        del self.validtokens[key]
        return False

    def __getitem__(self, key):
        return self.get(key, BibUserCacheDic({}, on_set_bind_to=(self, key)))

    def __setitem__(self, key, val):
        super(BibUserCacheDic, self).__setitem__(key, _to_bibusercacheobj(val))
        self._do_pending_bind()
        # assume that we __setitem__ is called, the value is up-to-date, ie. update the
        # corresponding validtoken.
        self.validtokens[key] = self.validtoken_fn(val)

    def setdefault(self, key, val):
        super(BibUserCacheDic, self).setdefault(key, _to_bibusercacheobj(val))
        self._do_pending_bind()

    def update(self, *args, **kwargs):
        # Problem: we need to make sure each value is filtered with _to_bibusercacheobj(val)
        # ###: Wait, doesn't dict.update() call __setitem__() for each item?
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

    def __setstate__(self, state):
        self.clear()
        if not 'cache' in state or 'validtokens' in state:
            # invalid cache
            logger.debug("Ignoring invalid cache")
            return

        cache = state['cache']
        validtokens = state['validtokens']
        for k,v in cache.iteritems():
            self[k] = v
            self.validtokens[k] = validtokens.get(k,None)

    def __getstate__(self):
        state = {
            'cache': {}
            'validtokens': {}
            }
        for k,v in self.iteritems():
            state['cache'][k] = v
            state['validtokens'][k] = self.validtokens.get(k, None)

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

