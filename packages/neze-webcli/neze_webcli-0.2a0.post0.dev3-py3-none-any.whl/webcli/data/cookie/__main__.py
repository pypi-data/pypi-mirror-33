from . import Cookie
from ._names import _get_cookie_jar
from random import randint

print('COOKIE',_get_cookie_jar())
ckie = Cookie('cookie-test')
print(ckie.filename)

value=hex(randint(0,65535))
key1='foo'
key2='bar.foo'
key3=('bar','bar')

print('---- old ----')
print(ckie.get(key1))
print(ckie.get(key2))
print(ckie.get(key3))

print('---- new ----')
ckie[key1] = value
ckie.set(key2,value)
ckie.set(key3,value)

print(value)
