
from __future__ import print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)



def assert_entries_equal(self, e1, e2, **kwargs):
    
    self.assertEqual(e1.type, e2.type)

    for role in 'author', 'editor':
        self.assertEqual(role in e1.persons, role in e2.persons)
        if role in e1.persons:
            self.assertListEqual(e1.persons[role], e2.persons[role])
    
    self.assertDictEqual(dict(e1.fields), dict(e2.fields), **kwargs)
        



def assert_keyentrylists_equal(self, l1, l2):

    #logger.debug("assert_keyentrylists_equal (%d,%d)"%(len(l1),len(l2)))

    self.assertEqual(len(l1), len(l2), msg="List lengths differ!")

    for n in range(len(l1)):

        self.assertEqual(len(l1[n]), 2, msg="Entry #{} isn't 2-tuple".format(n))
        self.assertEqual(len(l2[n]), 2, msg="Entry #{} isn't 2-tuple".format(n))

        #logger.debug("Checking entry (%s,%s)"%(l1[n][0],l1[n][1]))

        self.assertEqual(l1[n][0], l2[n][0],
                         msg="Entry keys differ {!r} != {!r}".format(l1[n][0],l2[n][0]))
        assert_entries_equal(self, l1[n][1], l2[n][1],
                             msg="Entry #{} key={}".format(n, l1[n][0]))
