
import re
import argparse

import filters



def getbool(x):
    try:
        return (int(x) != 0)
    except TypeError, ValueError:
        pass
    if (isinstance(x, basestring)):
        m = re.match(r'^\s*(t(?:rue)?|1|y(?:es)?|on)\s*$', x, re.IGNORECASE);
        if m:
            return True
        m = re.match(r'^\s*(f(?:alse)?|0|n(?:o)?|off)\s*$', x, re.IGNORECASE);
        if m:
            return False
    raise ValueError("Can't parse boolean value: %r" % x);
            



class store_or_count(argparse.Action):
    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        # some checks
        if nargs != '?':
            raise ValueError('store_or_const: nargs must be "?"');
        
        super(store_or_count, self).__init__(option_strings, dest, nargs=nargs, const=None, **kwargs);


    def __call__(self, parser, namespace, values, option_string):

        try:
            val = getattr(namespace, self.dest);
        except AttributeError:
            val = 0;

        if (values is not None):
            # value provided
            val = int(values);
        else:
            val += 1;
        
        setattr(namespace, self.dest, val);



rxkeyval = re.compile(r'^([\w.-]+)=(.*)$', re.DOTALL);

class store_key_val(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_val actions must be == 1')

        super(store_key_val, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            **kwargs);


    def __call__(self, parser, namespace, values, option_string):
        # parse key-value pair in values
        if (isinstance(values, list)):
            values = values[0];
        m = rxkeyval.match(values);
        if not m:
            raise ValueError("cannot parse key=value pair: "+repr(values));

        keyvalpair = (m.group(1), m.group(2),)

        if (not self.dest):
            (key, val) = keyvalpair;
            setattr(namespace, key, val);
        else:
            try:
                d = getattr(namespace, self.dest);
            except AttributeError:
                pass
            if not d:
                d = [];
            d.append(keyvalpair);
            setattr(namespace, self.dest, d);



class store_key_const(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, const=True, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_const actions must be == 1')

        super(store_key_const, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            **kwargs);


    def __call__(self, parser, namespace, values, option_string):

        key = values[0]

        if (not self.dest):
            setattr(namespace, key, self.const);
        else:
            try:
                d = getattr(namespace, self.dest);
            except AttributeError:
                d = [];
            d.append(key);
            setattr(namespace, self.dest, d);


class opt_action_help(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        if (not values):
            parser.print_help()
            parser.exit()

        thefilter = values

        filters.print_filter_help(thefilter);
        parser.exit();
