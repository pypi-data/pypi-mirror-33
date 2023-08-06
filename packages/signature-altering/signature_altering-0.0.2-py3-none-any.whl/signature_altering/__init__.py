'''signature_altering -- create signature-altering decorators

This package is for creating decorators that alter the signatures of
decorated functions in predictable ways, namely inserting/removing
arguments from the fromt and inserting/removing keyword arguments.

>>> # use case 1: preserve signature
>>> @decorator
... def foo1(f, *args, **kwargs):
...     print('calling', f.__name__)
...     return f(*args, **kwargs)
...
>>> @foo1
... def bar1(x, y, z):
...     print(x, y, z)
...
>>> print(signature(bar1))
(x, y, z)
>>> bar1(1, 2, 3)
calling bar1
1 2 3
>>> # use case 2: the decorator inserts one or more arguments to the wrapped function
>>> @decorator(insert_args=1)
... def foo2(f, *args, **kwargs):
...     print('calling', f.__name__, 'with special parameter')
...     return f(42, *args, **kwargs)
...
>>> @foo2
... def bar2(x, y, z):
...     print(x, y, z)
...
>>> print(signature(bar2))
(y, z)
>>> bar2(2, 3)
calling bar2 with special parameter
42 2 3
>>> # use case 3: the decorator accepts one or more arguments that are not passed to the wrapped function
>>> @decorator
... def foo3(f, x, *args, **kwargs):
...     print('calling', f.__name__, 'first argument was', x)
...     return f(*args, **kwargs)
...
>>> @foo3
... def bar3(y, z):
...     print(y, z)
...
>>> print(signature(bar3))
(x, y, z)
>>> bar3(1, 2, 3)
calling bar3 first argument was 1
2 3
>>> # use case 4: the decorator inserts one or more keyword arguments to the wrapped function
>>> @decorator(insert_kwargs='y')
... def foo4(f, *args, **kwargs):
...     print('calling', f.__name__, 'with special parameter')
...     return f(*args, y=42, **kwargs)
...
>>> @foo4
... def bar4(x, y, z):
...     print(x, y, z)
...
>>> print(signature(bar4))
(x, *, z)
>>> bar4(1, z=3)
calling bar4 with special parameter
1 42 3
>>> # use case 5: the decorator accepts one or more keyword arguments that are not passed to the wrapped function
>>> @decorator
... def foo5(f, *args, y, **kwargs):
...     print('calling', f.__name__, 'with y =', y)
...     return f(*args, **kwargs)
...
>>> @foo5
... def bar5(z):
...    print(z)
...
>>> print(signature(bar5))
(z, *, y)
>>> bar5(2, y=3)
calling bar5 with y = 3
2
>>> # use case 6: doing all of use case 2, 3, 4 and 5 at the same time
>>> @decorator(insert_args=2, insert_kwargs='a b')
... def foo6(f, x, *args, y, **kwargs):
...     print('calling', f.__name__, 'with x =', x, 'and y =', y)
...     return f(33, 44, *args, a=55, b=66, **kwargs)
...
>>> @foo6
... def bar6(x_, y_, z, a, b):
...    print(x_, y_, z, a, b)
...
>>> print(signature(bar6))
(x, z, *, y)
>>> bar6(11, y=22, z='z')
calling bar6 with x = 11 and y = 22
33 44 z 55 66
>>> def foo7(f):
...     @wraps(f, insert_kwargs='piew')
...     def __wrapped(blap, *args, **kwargs):
...         return f(*args, piew=blap, **kwargs)
...     __wrapped.dingdong = True
...     return __wrapped
...
>>> @foo7
... def bar7(a, piew):
...     return a ** piew
...
>>> print(signature(bar7))
(blap, a)
>>> bar7(2, 3)
9
>>> bar7.dingdong
True
'''

__version__ = '0.0.2'

from inspect import signature, Parameter
from functools import partial, wraps as _wraps, update_wrapper as _update_wrapper

def _get_parameters(f, kind_filter):
    if kind_filter is None:
        return list(signature(f).parameters.values())
    return [p for p in signature(f).parameters.values() if p.kind == kind_filter]

def _get_altered_signature(_decorator, insert_args, insert_kwargs, _decorated_fn, skip_args=0):
    sig_decorator_positional = _get_parameters(_decorator, Parameter.POSITIONAL_OR_KEYWORD)[skip_args:]
    sig_decorator_keyword = _get_parameters(_decorator, Parameter.KEYWORD_ONLY)
    insert_kwargs = frozenset(insert_kwargs.split())
    sig_decorated = list(sig_decorator_positional)
    popped_kwarg = False
    inserted_keyword_args = False
    for p in _get_parameters(_decorated_fn, None)[insert_args:]:
        if p.name in insert_kwargs:
            popped_kwarg = True
            continue
        if popped_kwarg and p.kind == p.POSITIONAL_OR_KEYWORD:
            p = p.replace(kind=p.KEYWORD_ONLY)
        if not inserted_keyword_args and p.kind in {p.VAR_POSITIONAL, p.VAR_KEYWORD}:
            inserted_keyword_args = True
            sig_decorated.extend(sig_decorator_keyword)
        sig_decorated.append(p)
    if not inserted_keyword_args:
        sig_decorated.extend(sig_decorator_keyword)
    return signature(_decorated_fn).replace(parameters=sig_decorated)

def decorator(_decorator=None, *, insert_args=0, insert_kwargs=''):
    '''replacement for decorator.decorator'''
    if _decorator is None:
        return partial(decorator, insert_args=insert_args, insert_kwargs=insert_kwargs)
    @_wraps(_decorator)
    def _decorator_wrapper(_decorated_fn):
        @_wraps(_decorated_fn)
        def _wrapper(*args, **kwargs):
            return _decorator(_decorated_fn, *args, **kwargs)
        _wrapper.__signature__ = _get_altered_signature(_decorator, insert_args, insert_kwargs, _decorated_fn, skip_args=1)
        return _wrapper
    s = signature(_decorator_wrapper)
    _decorator_wrapper.__signature__ = s.replace(parameters=[next(iter(s.parameters.values()))])
    return _decorator_wrapper

def update_wrapper(wrapper, _decorated_fn, *, insert_args=0, insert_kwargs=''):
    '''replacement for functools.update_wrapper'''
    sig = _get_altered_signature(wrapper, insert_args, insert_kwargs, _decorated_fn)
    _update_wrapper(wrapper, _decorated_fn)
    wrapper.__signature__ = sig
    return wrapper

def wraps(_decorated_fn, *, insert_args=0, insert_kwargs=''):
    '''replacement for functools.wraps'''
    return partial(update_wrapper, _decorated_fn=_decorated_fn, insert_args=insert_args, insert_kwargs=insert_kwargs)