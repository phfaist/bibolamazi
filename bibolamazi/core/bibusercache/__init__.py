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
import pickle
import traceback
import logging

import bibolamazi.init
from pybtex.database import Entry, Person
from bibolamazi.core.butils import call_with_args, BibolamaziError
from bibolamazi.core.bibusercache import tokencheckers

logger = logging.getLogger(__name__)




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
        return next( (key for key, val in self.parent.iteritems()
                      if val is self),
                     "<unknown>")

    def set_validation(self, tokenchecker, validate=True):
        """
        Set a function that will calculate the `token' for a given entry, for cache
        validation. The function `fn` shall compute a value based on a key (and possibly
        cache value) of the cache, such that comparision with `fncmp` (by default
        equality) will tell us if the entry is out of date. See the documentation for the
        :py:mod:`tokencheckers` modules for more information about cache validation.

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

        Invalid entries are deleted.

        Returns `True` if have valid item, otherwise `False`.
        """
        if not key in self.dic:
            # not valid anyway.
            logger.longdebug("validate_item(): %s: no such key %s", self._guess_name_for_dbg(), key)
            return False
        
        if not self.tokenchecker:
            # no validation
            logger.longdebug("validate_item(): %s[%s]: no validation set", self._guess_name_for_dbg(), key)
            return True

        logger.longdebug("Validating item `%s' in `%s', ...", key, self._guess_name_for_dbg())

        val = self.dic[key]
        ok = None
        try:
            ok = self.tokenchecker.cmp_tokens(key=key, value=val,
                                              oldtoken=self.tokens.get(key,None))
        except Exception as e:
            logger.debug("%s: Got exception in cmp_tokens(): ignoring and invalidating: %s", key, e)
            ok = False
        if ok:
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

    def new_value_set(self, key=None):
        """
        Informs the dic that the value for `key` has been updated, and a new validation
        token should be stored.

        If `key` is `None`, then this call is meant for the current object, so this call
        will relay to the parent dictionary.
        """
        self._do_pending_bind()

        if key is None:
            if not self.parent:
                logger.warning("BibUserCacheDic.new_value_set(): No parent set!")
            try:
                self.parent.new_value_set(next( (k for k,v in self.parent.iteritems()
                                                 if v is self) ))
            except StopIteration:
                logger.warning("BibUserCacheDic.new_value_set(): Can't find ourselves in parent!")

        if self.tokenchecker:
            self.tokens[key] = self.tokenchecker.new_token(key=key, value=self.dic.get(key))
            logger.longdebug("value changed in cache (key=%s), new value=%r, new token=%r", key, self.dic.get(key), self.tokens[key])
        if self.parent:
            self.parent.child_notify_changed(self)
                

    def __getitem__(self, key):
        return self.dic.get(key, BibUserCacheDic({}, parent=self, on_set_bind_to_key=key))

    def __setitem__(self, key, val):
        self.dic[key] = _to_bibusercacheobj(val, parent=self)
        self._do_pending_bind()
        # assume that we __setitem__ is called, the value is up-to-date, ie. update the
        # corresponding token.
        self.new_value_set(key)

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
        self._do_changing_operation(None, deltheitem)

    def __contains__(self, value):
        return value in self.lst

    def __len__(self):
        return len(self.lst)

    def insert(self, index, value):
        self._do_changing_operation(value, lambda x: self.lst.insert(index, x))

    def append(self, value):
        self._do_changing_operation(value, lambda x: self.lst.append(x))

    def __setitem__(self, key, val):
        self._do_changing_operation(val, lambda x: self.lst.__setitem__(key, x))

    def _do_changing_operation(self, val, fn):
        ret = fn(None if val is None else _to_bibusercacheobj(val, parent=self))
        if self.parent:
            self.parent.child_notify_changed(self)
        return ret
    
    def __repr__(self):
        return 'BibUserCacheList(%r)' %(self.lst)



class BibUserCache(object):
    """
    The basic root cache object.

    This object stores the corresponding cache dictionaries for each cache. (See
    :py:meth:`cacheFor`.)

    (Internally, the caches are stored in one root :py:class:`BibUserCacheDic`.)
    """
    def __init__(self, cache_version=None):
        logger.longdebug("BibUserCache: Constructor!")
        self.cachedic = BibUserCacheDic({})
        self.entry_validation_checker = tokencheckers.TokenCheckerPerEntry()
        self.comb_validation_checker = tokencheckers.TokenCheckerCombine(
            tokencheckers.VersionTokenChecker(cache_version),
            self.entry_validation_checker,
            )
        self.cachedic.set_validation(self.comb_validation_checker)
        # an instance of an expiry_checker that several entries might share in
        # self.entry_validation_checker.
        self.expiry_checker = tokencheckers.TokenCheckerDate()

    def setDefaultInvalidationTime(self, time_delta):
        """
        A timedelta object giving the amount of time for which data in cache is consdered
        valid (by default).
        """
        self.expiry_checker.set_time_valid(time_delta)


    def cacheFor(self, cache_name):
        """
        Returns the cache dictionary object for the given cache name. If the cache
        dictionary does not exist, it is created.
        """
        if not cache_name in self.cachedic:
            self.cachedic[cache_name] = {}

        return self.cachedic[cache_name]


    def cacheExpirationTokenChecker(self):
        """
        Returns a cache expiration token checker validator which is configured with the
        default cache invalidation time.

        This object may be used by subclasses as a token checker for sub-caches that need
        regular invalidation (typically several days in the default configuration).

        Consider using though `installCacheExpirationChecker()`, which simply applies a
        general validator to your full cache; this is generally what you might want.
        """
        return self.expiry_checker
    

    def installCacheExpirationChecker(self, cache_name):
        """
        Installs a cache expiration checker on the given cache.

        This is a utility that is at the disposal of the cache accessors to easily set up
        an expiration validator on their caches. Also, a single instance of an expiry
        token checker (see `TokenCheckerDate`) is shared between the different sub-caches
        and handled by this main cache object.

        The duration of the expiry is typically several days; because the token checker
        instance is shared this cannot be changed easily nor should it be relied upon. If
        you have custom needs or need more control over this, create your own token
        checker.

        Returns: the cache dictionary. This may have changed to a new empty object if the
        cache didn't validate!

        WARNING: the cache dictionary may have been altered with the validation of the
        cache! Use the return value of this function, or call
        :py:meth:`BibUserCacheAccessor.cacheDic` again!

        Note: this validation will not validate individual items in the cache dictionary,
        but the dictionary as a whole. Depending on your use case, it might be worth
        introducing per-entry validation. For that, check out the various token checkers
        in :py:mod:`.tokencheckers` and call
        :py:meth:`~core.bibusercache.BibUserCacheDic.set_validation` to install a
        specific validator instance.
        """
        if not cache_name in self.cachedic:
            raise ValueError("Invalid cache name: %s"%(cache_name))
        
        # normal thing, i.e. the cache expires after N days
        if not self.entry_validation_checker.has_entry_for(cache_name):
            logger.longdebug("Adding expiry checker for %s", cache_name)
            self.entry_validation_checker.add_entry_check(cache_name, self.expiry_checker)
            self.cachedic.validate_item(cache_name)

        return self.cacheFor(cache_name)



    def hasCache(self):
        """
        Returns `True` if we have any cache at all. This only returns `False` if there are
        no cache dictionaries defined.
        """
        return bool(self.cachedic)

    def loadCache(self, cachefobj):
        """
        Load the cache from a file-like object `cachefobj`.

        This tries to unpickle the data and restore the cache. If the loading fails, e.g. 
        because of an I/O error, the exception is logged but ignored, and an empty cache
        is initialized.

        Note that at this stage
        only the basic validation is performed; the cache accessors should then each
        initialize their own subcaches with possibly their own specialized validators.
        """
        try:
            data = pickle.load(cachefobj);
            self.cachedic = data['cachedic']
        except Exception as e:
            logger.longdebug("EXCEPTION IN pickle.load():\n%s", traceback.format_exc())
            logger.debug("IGNORING EXCEPTION IN pickle.load(): %s.", e)
            self.cachedic = BibUserCacheDic({})
            pass
        
        self.cachedic.set_validation(self.comb_validation_checker)

    def saveCache(self, cachefobj):
        """
        Saves the cache to the file-like object `cachefobj`. This dumps a pickle-d version
        of the cache information into the stream.
        """
        data = {
            # cache pickle versions for Bibolamazi versions:
            #   --1.4:  <no information saved, incompatible>
            #   1.5+:   1
            #   2.x :   2
            'cachepickleversion': 2,
            'cachedic': self.cachedic,
            }
        logger.longdebug("Saving cache. Cache keys are: %r", self.cachedic.dic.keys())
        pickle.dump(data, cachefobj, protocol=2);






# ------------------------------------------------------------------------------


class BibUserCacheError(BibolamaziError):
    """
    An exception which occurred when handling user caches. Usually, problems in the cache
    are silently ignored, because the cache can usually be safely regenerated.

    However, if there is a serious error which prevents the cache from being regenerated,
    for example, then this error should be raised.
    """

    def __init__(self, cache_name, message):
        if (not isinstance(cache_name, basestring)):
            cache_name = '<unknown>'
        super(BibUserCacheError, self).__init__(u"Cache `"+cache_name+u"': "+unicode(message))
        self.cache_name = cache_name
        self.message = message




class BibUserCacheAccessor(object):
    """
    Base class for a cache accessor.

    Filters should access the bibolamazi cache through a *cache accessor*. A cache
    accessor organizes how the caches are used and maintained. This is needed since
    several filters may want to access the same cache (e.g. fetched arXiv info from the
    arxiv.org API), so it is necessary to abstract out the cache object and how it is
    maintained out of the filter. This also avoids issues such as which filter is
    responsible for creating/refreshing the cache, etc.

    A unique accessor instance is attached to a particular cache name
    (e.g. 'arxiv_info'). It is instantiated by the BibolamaziFile. It is instructed to
    initialize the cache, possibly install token checkers, etc. at the beginning, before
    running any filters. The accessor is free to handle the cache as it prefers--build it
    right away, refresh it on demand only, etc.

    Filters access the cache by requesting an instance to the accessor. This is done by
    calling :py:meth:`~core.bibolamazifile.BibolamaziFile.cache_accessor` (you can use
    :py:meth:`~core.bibfilter.BibFilter.bibolamaziFile` to get a pointer to the
    `bibolamazifile` object.). Filters should declare in advance which caches they would
    like to have access to by reimplementing the
    :py:meth:`~core.bibfilter.BibFilter.requested_cache_accessors` method.

    Accessors are free to implement their public API how they deem it best. There is no
    obligation or particular structure to follow. (Although `refresh_cache()`,
    `fetch_missing_items(list)`, or similar function names may be typical.)

    Cache accessor objects are instantiated by the bibolamazi file. Their constructors
    should accept a keyword argument `bibolamazifile` and pass it on to the superclass
    constructor. Constructors should also accept `**kwargs` for possible compatibility
    with future additions and pass it on to the parent constructor. The `cache_name`
    argument of this constructor should be a fixed string passed by the subclass,
    identifying this cache (e.g. 'arxiv_info').
    """
    def __init__(self, cache_name, bibolamazifile, **kwargs):
        super(BibUserCacheAccessor, self).__init__(**kwargs)
        self._cache_name = cache_name
        self._bibolamazifile = bibolamazifile
        self._cache_obj = None


    def initialize(self, cache_obj):
        """
        Initialize the cache.

        Subclasses should perform any initialization tasks, such as install *token
        checkers*. This function should not return anything.

        Note that it is *strongly* recommended to install some form of cache invalidation,
        would it be just even an expiry validator. You may want to call
        :py:meth:`~core.bibusercache.BibUserCache.installCacheExpirationChecker` on
        `cache_obj`.

        Note that the order in which the `initialize()` method of the various caches is
        called is undefined.

        Use the :py:meth:`cacheDic` method to access the cache dictionary. Note that if
        you install token checkers on this cache, e.g. with
        `cache_obj.installCacheExpirationChecker()`, then the cache dictionary object may
        have changed! (To be sure, call :py:meth:`cacheDic` again.)

        The default implementation raises a `NotImplemented` exception.
        """
        raise NotImplemented("Subclasses of BibUserCacheAccess must reimplement initialize()")


    def cacheName(self):
        """
        Return the cache name, as set in the constructor.

        Subclasses do not need to reimplement this function.
        """
        return self._cache_name


    def cacheDic(self):
        """
        Returns the cache dictionary. This is meant as a 'protected' method for the
        accessor only. Objects that query the accessor should use the accessor-specific
        API to access data.

        The cache dictionary is a :py:class:`BibUserCacheDic` object. In particular,
        subcaches may want to set custom token checkers for proper cache invalidation
        (this should be done in the :py:meth:`initialize` method).

        This returns the data in the cache object that was set internally by the
        :py:class:`BibolamaziFile` via the method :py:meth:`setCacheObj`. Don't call
        that manually, though, unless you're implementing an alternative
        :py:class:`BibolamaziFile` class !
        """
        return self._cache_obj.cacheFor(self.cacheName())


    def cacheObject(self):
        """
        Returns the parent :py:class:`BibUserCache` object in which :py:meth:`cacheDic`
        is a sub-cache. This is provided FOR CONVENIENCE! Don't abuse this!

        You should never need to access the object directly. Maybe just read-only to get
        some standard attributes such as the root cache version. If you're writing
        directly to the root cache object, there is most likely a design flaw in your
        code!

        Most of all, don't write into other sub-caches!!
        """
        return self._cache_obj


    def setCacheObj(self, cache_obj):
        """
        Sets the cache dictionary and cache object that will be returned by `cacheDic()`
        and `cacheObject()`, respectively. Accessors and filters should not call (nor
        reimplement) this function. This function gets called by the `BibolamaziFile`.
        """
        self._cache_obj = cache_obj

    def bibolamaziFile(self):
        """
        Returns the parent bibolamazifile of this cache accessor. This may be useful,
        e.g. to initialize a token cache validator in `initialize()`.

        Returns the object given in the constructor argument. Do not reimplement this
        function.
        """
        return self._bibolamazifile
