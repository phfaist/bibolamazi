
from __future__ import print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)

from pybtex.database import Entry, Person, BibliographyData



# see https://stackoverflow.com/a/15868615/1694896

def fmt_dbg_entry(e, linefmt='    {field}: "{value}"'):
    allfields = list(e.fields.items())
    for role in ('editor', 'author'):
        if role in e.persons:
            alist = [str(a) for a in e.persons[role]]
            allfields = [ (role, "; ".join(alist)) ] + allfields

    return "\n".join([ linefmt.format(field=f,value=v) for f,v in allfields ])


class CustomAssertions(object):

    def assertEqual(self, a, b, msg=None):
        if isinstance(a, Entry) and isinstance(b, Entry):
            self.assert_entries_equal(a, b)

        if isinstance(a, BibliographyData) and isinstance(b, BibliographyData):
            self.assert_keyentrylists_equal(list(a.entries.items()), list(b.entries.items()), msg=msg)

        return super(CustomAssertions, self).assertEqual(a, b, msg=msg)


    def assert_entries_equal(self, e1, e2, **kwargs):

        self.assertEqual(e1.type, e2.type)

        for role in 'author', 'editor':
            self.assertEqual(role in e1.persons, role in e2.persons,
                             msg="mismatch in presence of persons role '{}'".format(role))
            if role in e1.persons:
                self.assertListEqual(e1.persons[role], e2.persons[role])

        self.assertDictEqual(dict(e1.fields), dict(e2.fields), **kwargs)


    def assert_keyentrylists_equal(self, l1, l2, order=True, msg=None):

        #logger.debug("assert_keyentrylists_equal (%d,%d)"%(len(l1),len(l2)))

        def domsg(x, msg=msg):
            if msg:
                return x + '\n --- ' + msg
            return x

        if not order:
            # if order doesn't count, then sort both lists according to key
            l1 = sorted(l1, key=lambda x: x[0])
            l2 = sorted(l2, key=lambda x: x[0])

        if len(l1) != len(l2):
            # find which keys are not in each other's lists
            kl1 = set(dict(l1).keys())
            kl2 = set(dict(l2).keys())
            common = kl1 & kl2
            raise self.failureException(domsg(("List lengths differ, {} != {}.\n"
                                               "Keys in 1 not in 2 = {!r}\n"
                                               "Keys in 2 not in 1 = {!r}")
                                              .format(len(l1), len(l2), kl1 - common, kl2 - common)))

        for n in range(len(l1)):

            self.assertEqual(len(l1[n]), 2, msg=domsg("Entry #{} isn't 2-tuple".format(n)))
            self.assertEqual(len(l2[n]), 2, msg=domsg("Entry #{} isn't 2-tuple".format(n)))

            #logger.debug("Checking entry (%s,%s)"%(l1[n][0],l1[n][1]))

            self.assertEqual(l1[n][0], l2[n][0],
                             msg=domsg("Entry keys differ {!r} != {!r}".format(l1[n][0],l2[n][0])))
            self.assert_entries_equal(l1[n][1], l2[n][1],
                                      msg=domsg("Entry #{} '{}' differs".format(n, l1[n][0])))
