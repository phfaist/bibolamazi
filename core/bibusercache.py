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

import collections
import inspect
import datetime
import pickle
import hashlib

from pybtex.database import Entry
from core.blogger import logger
from core.butils import call_with_args


class TokenChecker(object):
    def __init__(self, **kwargs):
        super(TokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        return True

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        # by default, compare for equality.
        newtoken = self.new_token(key=key, value=value, **kwargs)
        if newtoken == oldtoken:
            #logger.longdebug("Basic cmp_tokens: newtoken=%r, oldtoken=%r ---> OK", newtoken, oldtoken)
            return True
        #logger.longdebug("Basic cmp_tokens: newtoken=%r, oldtoken=%r ---> DIFFERENT", newtoken, oldtoken)
        return False


class TokenCheckerDate(TokenChecker):
    def __init__(self, time_valid=datetime.timedelta(days=3), **kwargs):
        super(TokenCheckerDate, self).__init__(**kwargs)
        self.time_valid = time_valid

    def set_time_valid(self, time_valid):
        self.time_valid = time_valid

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        now = datetime.datetime.now()
        #logger.longdebug("Comparing %r with %r; time_valid=%r", now, oldtoken, self.time_valid)
        if oldtoken is None:
            return False
        return ((now - oldtoken) < self.time_valid)

    def new_token(self, **kwargs):
        return datetime.datetime.now()


class TokenCheckerCombine(TokenChecker):
    def __init__(self, *args, **kwargs):
        super(TokenCheckerCombine, self).__init__(**kwargs)
        self.subcheckers = args

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
        for k in range(len(self.subcheckers)):
            chk = self.subcheckers[k]
            #logger.longdebug("TokenCheckerCombine: cmp_tokens(): #%d: %r : key=%s value=... oldtoken=%r",
            #                 k, chk, key, oldtoken[k])
            if not chk.cmp_tokens(key=key, value=value, oldtoken=oldtoken[k], **kwargs):
                return False
        return True

    def new_token(self, key, value, **kwargs):
        return  tuple( (chk.new_token(key=key, value=value, **kwargs) for chk in self.subcheckers) )


class TokenCheckerPerEntry(TokenChecker):
    def __init__(self, checkers={}, **kwargs):
        super(TokenCheckerPerEntry, self).__init__(**kwargs)
        self.checkers = checkers

    def add_entry_check(self, key, checker):
        """
        Add an entry-specific checker.

        Note that no explicit validation is performed. (This can't be done because we
        don't even have a pointer to the cache dict.) So you should call manually
        `BibUserCacheDict.validate_item()`
        """
        if not checker:
            raise ValueError("add_entry_check(): may not provide `None`")
        if key in self.checkers:
            if self.checkers[key] is checker:
                return # already set
            logger.warning("TokenCheckerPerEntry: Replacing checker for `%s'", key)
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




class EntryFieldsTokenChecker(TokenChecker):
    def __init__(self, bibdata, fields=[], store_type=False, store_persons=[], **kwargs):
        self.bibdata = bibdata
        self.fields = fields
        self.store_type = store_type
        self.store_persons = store_persons
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
    def __init__(self, this_version, **kwargs):
        super(VersionTokenChecker, self).__init__(**kwargs)
        self.this_version = this_version

    def new_token(self, key, value, **kwargs):
        return self.this_version







def _to_bibusercacheobj(obj, parent):
    if (isinstance(obj, BibUserCacheDic) or isinstance(obj, BibUserCacheList)):
        # make sure we don't make copies of these objects, but keep references
        # to the original instance. Especially important for the on_set_bind_to
        # feature.
        obj.set_parent(parent)
        return obj
    if (isinstance(obj, dict)):
        return BibUserCacheDic(obj, parent=parent)
    if (isinstance(obj, list)):
        return BibUserCacheList(obj, parent=parent)
    return obj





class BibUserCacheDic(collections.MutableMapping):
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
        self._init_empty(on_set_bind_to_key=kwargs.pop('on_set_bind_to_key', None),
                         parent = kwargs.pop('parent', None))

        # by default, no validation.
        self.tokenchecker = None
        
        self.update(dict(*args, **kwargs))

    def _init_empty(self, on_set_bind_to_key=None, parent=None):
        self.dic = {}
        self.tokens = {}
        self.tokenchecker = None
        self._on_set_bind_to_key = on_set_bind_to_key
        self.parent = parent

    def _guess_name_for_dbg(self):
        if not self.parent:
            return "<root>"
        for key, val in self.parent.iteritems():
            if val == self:
                return key
        return "<unknown>"

    def set_validation(self, tokenchecker, validate=True):
        """
        Set a function that will calculate the `token' for a given entry, for cache
        validation. The function `fn` shall compute a value based on a key (and possibly
        cache value) of the cache, such that comparision with `fncmp` (by default
        equality) will tell us if the entry is out of date. *********TODO: BETTER DOC
        **************

        If `validate` is `True`, then we immediately validate the contents of the cache.
        """

        if self.tokenchecker is tokenchecker:
            # no change
            return

        # store this token checker
        self.tokenchecker = tokenchecker

        # this counts as a change, so save it
        self._do_pending_bind()

        if validate:
            self.validate()

    def validate(self):
        """
        Validate this whole dictionary, i.e. make sure that each entry is still valid.

        This calls `validate_item()` for each item in the dictionary.
        """

        keylist = self.dic.keys()

        for key in keylist:
            self.validate_item(key)

    def validate_item(self, key):
        """
        Validate an entry of the dictionary manually. Usually not needed.

        If the value is valid, and happens to be a BibUserCacheDic, then that dictionary
        is also validated.

        Returns `True` if have valid item, otherwise `False`.
        """
        if not key in self.dic:
            # not valid anyway.
            #logger.longdebug("validate_item(): %s: no such key %s", self._guess_name_for_dbg(), key)
            return False
        
        if not self.tokenchecker:
            # no validation
            #logger.longdebug("validate_item(): %s[%s]: no validation set", self._guess_name_for_dbg(), key)
            return True

        logger.longdebug("Validating item `%s' in `%s', ...", key, self._guess_name_for_dbg())

        val = self.dic[key]
        if self.tokenchecker.cmp_tokens(key=key, value=val,
                                        oldtoken=self.tokens.get(key,None)):
            if isinstance(val, BibUserCacheDic):
                #logger.longdebug("Validating sub-dictionary `%s' ...", key)
                val.validate()
                # still return True independently of what happens in val.validate(),
                # because this dictionary is still valid.
            logger.longdebug("Cache item `%s' is valid; keeping", key)
            return True

        # otherwise, invalidate the cache. Don't just set to None or {} or [] because we
        # don't know what type the value is. This way is safe, because if getitem is
        # called, automatically an empty dic will be created.
        logger.longdebug("Cache item `%s' is NO LONGER VALID; trashing.", key)
        del self.dic[key]
        if key in self.tokens:
            del self.tokens[key]
        return False

    def __getitem__(self, key):
        return self.dic.get(key, BibUserCacheDic({}, parent=self, on_set_bind_to_key=key))

    def __setitem__(self, key, val):
        self.dic[key] = _to_bibusercacheobj(val, parent=self)
        self._do_pending_bind()
        # assume that we __setitem__ is called, the value is up-to-date, ie. update the
        # corresponding token.
        if self.tokenchecker:
            self.tokens[key] = self.tokenchecker.new_token(key=key, value=val)
        if self.parent:
            self.parent.child_notify_changed(self)


    def __delitem__(self, key):
        del self.dic[key]
        if key in self.tokens:
            del self.tokens[key]
        if self.parent:
            self.parent.child_notify_changed(self)

    def iteritems(self):
        return self.dic.iteritems()

    def __iter__(self):
        return iter(self.dic)

    def __len__(self):
        return len(self.dic)

    def __contains__(self, key):
        return key in self.dic


    def child_notify_changed(self, obj):
        # update cache validation tokens for this object
        if self.tokenchecker:
            for key, val in self.dic.iteritems():
                if val is obj:
                    self.tokens[key] = self.tokenchecker.new_token(key=key, value=val)
                    # don't break, as it could be that the same object is pointed to by
                    # different keys... so complete the for loop
        
        if self.parent:
            self.parent.child_notify_changed(self)

    def set_parent(self, parent):
        self.parent = parent

    def _do_pending_bind(self):
        if (self._on_set_bind_to_key is not None and
            self.parent is not None):
            #
            self.parent[self._on_set_bind_to_key] = self
            self._on_set_bind_to_key = None

    def __repr__(self):
        return 'BibUserCacheDic(%r)' %(self.dic if hasattr(self,'dic') else {})

    def __setstate__(self, state):
        #logger.longdebug("Set state to empty; loading state=%r", state)

        self._init_empty()

        if not ('cache' in state and 'tokens' in state and 'parent' in state):
            # invalid cache
            logger.debug("Ignoring invalid cache")
            return

        self.parent = state['parent']
        self.dic = state['cache']
        self.tokens = state['tokens']


    def __getstate__(self):
        state = {
            'parent': self.parent,
            'cache': self.dic,
            'tokens': self.tokens,
            }
        return state



class BibUserCacheList(collections.MutableSequence):
    def __init__(self, *args, **kwargs):
        self.lst = []
        self.parent = kwargs.pop('parent', None)
        for x in list(*args, **kwargs):
            self.append(x)

    def __getitem__(self, index):
        return self.lst[index]

    def __delitem__(self, index):
        def deltheitem(value=None):
            del self.lst[index]
        self._do_changing_operation(self, None, deltheitem)

    def __contains__(self, value):
        return value in self.lst

    def __len__(self):
        return len(self.lst)

    def insert(self, index, value):
        self._do_changing_operation(self, value, lambda x: self.lst.insert(index, x))

    def append(self, value):
        self._do_changing_operation(self, value, lambda x: self.lst.append(x))

    def __setitem__(self, key, val):
        self._do_changing_operation(self, val, lambda x: self.lst.__setitem__(key, x))

    def _do_changing_operation(self, val, fn):
        ret = fn(None if val is None else _to_bibusercacheobj(val))
        if self.parent:
            self.parent.child_notify_changed(self)
        return ret
    
    def __repr__(self):
        return 'BibUserCacheList(%r)' %(self.lst)



class BibUserCache(object):
    def __init__(self, cache_version=None):
        self.cachedic = BibUserCacheDic({})
        self.entry_validation_checker = TokenCheckerPerEntry()
        self.comb_validation_checker = TokenCheckerCombine(VersionTokenChecker(cache_version),
                                                           self.entry_validation_checker,
                                                           )
        self.cachedic.set_validation(self.comb_validation_checker)
        # an instance of an expiry_checker that several entries might share in
        # self.entry_validation_checker.
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

        #logger.longdebug("cache_for(%r, dont_expire=%r)", cachename, dont_expire)

        if not dont_expire:
            # normal thing, i.e. the cache expires after N days
            if not self.entry_validation_checker.has_entry_for(cachename):
                logger.longdebug("Adding expiry checker for %s", cachename)
                self.entry_validation_checker.add_entry_check(cachename, self.expiry_checker)
                self.cachedic.validate_item(cachename)
        elif self.entry_validation_checker.has_entry_for(cachename):
            # conflict: twice cache requested with conflicting values of dont_expire
            raise RuntimeError("Conflicting values of dont_expire given for cache `%s'"%(cachename))

        return self.cachedic[cachename]


    def has_cache(self):
        return bool(self.cachedic)

    def load_cache(self, cachefobj):
        try:
            data = pickle.load(cachefobj);
            self.cachedic = data['cachedic']
        except Exception as e:
            logger.debug("IGNORING EXCEPTION IN pickle.load(): %s.", e)
            pass
        
        self.cachedic.set_validation(self.comb_validation_checker)

    def save_cache(self, cachefobj):
        data = {
            'cachepickleversion': 1,
            'cachedic': self.cachedic,
            }
        pickle.dump(data, cachefobj, protocol=2);

