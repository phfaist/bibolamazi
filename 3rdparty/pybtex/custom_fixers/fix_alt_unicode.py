# Taken from jinja2. Thanks, Armin Ronacher.
# See also http://lucumr.pocoo.org/2010/2/11/porting-to-python-3-a-guide


from lib2to3 import fixer_base


class FixAltUnicode(fixer_base.BaseFix):
    PATTERN = "'__unicode__'"

    def transform(self, node, results):
        new = node.clone()
        new.value = '__str__'
        return new
