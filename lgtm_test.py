

# why do we get py/modification-of-default-value ?

def with_default_value(y=['a', 'b']):
    if isinstance(y, str):
        y = y.split() # here?
    print(y)

with_default_value()
with_default_value('x y z')
with_default_value()

# output looks good:
#
# ['a', 'b']
# ['x', 'y', 'z']
# ['a', 'b']



# ------------------------------------------------------------------------------


#
# Alert py/non-iterable-in-for-loop does not seem to be raised consistently.
#

# It's not raised here, where 'values' could be anything that was passed to this
# function
def might_not_be_iterator(values):
    return [x[0] for x in values]

mylist = might_not_be_iterator([(1,'One'), (2,'Two'), (199,'OneHundredAndNinetyNine')])


# But it's raised here in similar circumstances (only that it is used to define
# an inner class member)
def make_enum_class(name, values):
    class TheEnumClass:
        _values = values
        _values_list = [x[0] for x in _values]
        # ...

    return TheEnumClass

MyEnumClass = make_enum_class('MyEnumClass', [(1,'One'), (2,'Two'), (199,'OneHundredAndNinetyNine')])

