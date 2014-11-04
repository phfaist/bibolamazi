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


import datetime
import hashlib

from pybtex.database import Entry, Person
from core.blogger import logger




class TokenChecker(object):
    def __init__(self, **kwargs):
        super(TokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        return True

    def cmp_tokens(self, key, value, oldtoken, **kwargs):
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
        try:
            return ((now - oldtoken) < self.time_valid)
        except Exception as e:
            logger.debug("Got exception in TokenCheckerDate.cmp_tokens, probably not a datetime object: "
                         "ignoring and invalidating: %s", e)
            return False

    def new_token(self, **kwargs):
        return datetime.datetime.now()


class TokenCheckerCombine(TokenChecker):
    def __init__(self, *args, **kwargs):
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
    def __init__(self, bibdata, fields=[], store_type=False, store_persons=[], **kwargs):
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
    def __init__(self, this_version, **kwargs):
        super(VersionTokenChecker, self).__init__(**kwargs)
        self.this_version = this_version

    def new_token(self, key, value, **kwargs):
        return self.this_version


