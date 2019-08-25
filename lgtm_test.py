

# do we get py/modification-of-default-value ?

def with_default_value(x, y=['a', 'b']):
    if x:
        y = y[1:]

    print(x, y)

with_default_value(False)
with_default_value(True)
with_default_value(False)

# output looks good:
#
# False ['a', 'b']
# True ['b']
# False ['a', 'b']


# ------------------------------------------------------------------------------

def might_not_be_iterator(values):
    return [x[0] for x in values]

mylist = might_not_be_iterator([(1,'One'), (2,'Two'), (199,'OneHundredAndNinetyNine')])


def make_enum_class(name, values):
    class TheEnumClass:
        _values = values
        _values_list = [x[0] for x in _values]
        # (other attributes/methods unnecessary for this example)
    return TheEnumClass

MyEnumClass = make_enum_class('MyEnumClass', [(1,'One'), (2,'Two'), (199,'OneHundredAndNinetyNine')])

