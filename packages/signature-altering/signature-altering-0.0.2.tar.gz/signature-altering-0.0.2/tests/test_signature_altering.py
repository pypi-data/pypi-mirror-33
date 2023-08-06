import signature_altering
import doctest
from inspect import signature

def test_doctests():
    assert doctest.testmod(signature_altering, raise_on_error=True)[0] == 0

def test_decorated_vararg():
    @signature_altering.decorator
    def simple(f, *args, **kwargs):
        return f(*args, **kwargs)

    @simple
    def varargs(a, *args):
        return len(args)

    assert str(signature(varargs)) == '(a, *args)'
    assert varargs(10, 20, 30, 40) == 3