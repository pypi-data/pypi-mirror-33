import dill
import typing

def test_typing_basic():
    o = dill.copy(typing.Tuple)
    assert o == typing.Tuple
    t = typing.Tuple[typing.Callable, typing.Any]
    assert t == t.__origin__[t.__args__]
    ## >>> [k for k,v in vars(t).items() if v != vars(o)[k]]    
    ## ['__subclasshook__', '__args__', '__tree_hash__', '__origin__']
    l = typing.List[int]
    assert l == l.__origin__[l.__args__]
    u = typing.Union[int,str]
    assert u == u.__origin__[u.__args__]
    w = dill.copy(typing.GenericMeta)
    assert w == typing.GenericMeta
    assert isinstance(t, w)
    ### NOTE: the below are weird: isinstance raises a TypeError ###
    j = dill.copy(typing.Union)
    assert j == typing.Union
    assert repr(type(u)) == repr(j)
    # slightly less weird, but still weird
    a = dill.copy(typing.Any)
    assert a == typing.Any
    assert repr(type(a)) == repr(a)
    b = dill.copy(typing.Optional)
    assert b == typing.Optional
    assert repr(type(b)) == repr(b)
    h = dill.copy(typing.ClassVar)
    assert h == typing.ClassVar
    assert repr(type(h)) == repr(h)
    ### NOTE: more? https://docs.python.org/3/library/typing.html
    d = dill.copy(typing.NamedTuple)
    assert d == typing.NamedTuple
    assert type(d) == typing.NamedTupleMeta

def test_typing_annotations():
    def doit(x: int, y: typing.List[int]) -> typing.List[int]:
      return y + [x]
    
    _doit = dill.copy(doit)
    #assert sorted(doit.__annotations__.items()) == sorted(_doit.__annotations__.items())
    #assert _doit == doit

def test_typing_newtype():
    UserId = typing.NewType('UserId', int)
    _UserId = dill.copy(UserId)
    #assert _UserId.__qualname__ == UserId.__qualname__
    #assert _UserId == UserId

def test_typing_callable():
    q = typing.Callable[[int,str,typing.Any], typing.List[typing.Any]]
    assert q == q.__origin__[list(q.__args__[:-1]),q.__args__[-1]]
    c = typing.Callable[[int], None]
    assert c == c.__origin__[list(c.__args__[:-1]),c.__args__[-1]]
    p = typing.Callable[..., str]
    assert p == p.__origin__[p.__args__]
    w = dill.copy(typing.GenericMeta)
    assert w == typing.GenericMeta
    assert isinstance(q, w)

def test_typing_generic():
    T = typing.TypeVar('T')
    _T = dill.copy(T)
    #assert _T == T
    g = typing.Generic[T]
    assert g == g.__origin__[g.__args__]
    m = typing.Mapping[int,T]
    assert m == m.__origin__[m.__args__]
    i = typing.Iterable[T]
    assert i == i.__origin__[i.__args__]
    class User(object):
        pass
    U = typing.TypeVar('U', bound=User)
    _U = dill.copy(U)
    #assert _U == U
    e = typing.Type[U]
    assert e == e.__origin__[e.__args__]
    w = dill.copy(typing.GenericMeta)
    assert w == typing.GenericMeta
    assert isinstance(g, w)
    v = dill.copy(typing.TypeVar)
    assert v == typing.TypeVar
    assert isinstance(T, v)
    ### NOTE: needs work...
    s = dill.copy(typing.AnyStr)
    #assert s == typing.AnyStr
    assert isinstance(s, v)


if __name__ == '__main__':
    test_typing_basic()
    test_typing_annotations()
    test_typing_newtype()
    test_typing_callable()
    test_typing_generic()
