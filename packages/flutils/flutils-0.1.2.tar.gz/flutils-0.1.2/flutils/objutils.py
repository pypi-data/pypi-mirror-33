from typing import Any as _Any

from collections import (
    Iterator,
    KeysView,
    UserList,
    ValuesView,
    deque,
)

_LIST_LIKE = (
    list,
    set,
    frozenset,
    tuple,
    deque,
    Iterator,
    ValuesView,
    KeysView,
    UserList
)


def has_any_attrs(obj: _Any, *attrs: str) -> bool:
    """Check if the given ``obj`` has **ANY** of the given ``*attrs``.

    Args:
        obj (Any): The object to check.
        *attrs (str): The names of the attributes to check.

    Returns:
        bool: ``True`` if any of the given ``*attrs`` exist on the given
        ``obj``; otherwise, ``False``.

    Example:
        >>> from flutils import has_any_attrs
        >>> has_any_attrs(dict(),'get','keys','items','values','something')
        True
    """
    for attr in attrs:
        if hasattr(obj, attr) is True:
            return True
    return False


def has_any_callables(obj: _Any, *attrs: str) -> bool:
    """Check if the given ``obj`` has **ANY** of the given ``attrs`` and are
    callable.

    Args:
        obj (Any): The object to check.
        *attrs (str): The names of the attributes to check.

    Returns:
        bool: ``True`` if ANY of the given ``*attrs`` exist on
        the given ``obj`` and ANY are callable; otherwise, ``False``.

    Example:
        >>> from flutils import has_any_callables
        >>> has_any_callables(dict(),'get','keys','items','values','foo')
        True
    """
    if has_any_attrs(obj, *attrs) is True:
        for attr in attrs:
            if callable(getattr(obj, attr)) is True:
                return True
    return False


def has_attrs(
        obj: _Any,
        *attrs: str
) -> bool:
    """Check if given ``obj`` has all the given ``*attrs``.

    Args:
        obj (Any): The object to check.
        *attrs (str): The names of the attributes to check.

    Returns:
        bool: ``True`` if all the given ``*attrs`` exist on the given ``obj``;
        otherwise, ``False``.

    Example:
        >>> from flutils import has_attrs
        >>> has_attrs(dict(),'get','keys','items','values')
        True
    """
    for attr in attrs:
        if hasattr(obj, attr) is False:
            return False
    return True


# noinspection PyUnresolvedReferences
def has_callables(
        obj: _Any,
        *attrs: str
) -> bool:
    """Check if given ``obj`` has all the given ``attrs`` and are callable.

    Args:
        obj (Any): The object to check.
        *attrs (str): The names of the attributes to check.

    Returns:
        bool: ``True`` if all the given ``*attrs`` exist on the given
        ``obj`` and all are callable; otherwise, ``False``.

    Example:
        >>> from flutils import has_callables
        >>> has_callables(dict(),'get','keys','items','values')
        True
    """
    if has_attrs(obj, *attrs) is True:
        for attr in attrs:
            if callable(getattr(obj, attr)) is False:
                return False
        return True
    return False


def is_list_like(
        obj: _Any
) -> bool:
    """Check that given ``obj`` acts like a list and is iterable.

    List-like objects are instances of:

    - :obj:`UserList <collections.UserList>`
    - :obj:`Iterator <collections.abc.Iterator>`
    - :obj:`KeysView <collections.abc.KeysView>`
    - :obj:`ValuesView <collections.abc.ValuesView>`
    - :obj:`deque <collections.deque>`
    - :obj:`frozenset`
    - :obj:`list`
    - :obj:`set`
    - :obj:`tuple`

    List-like objects are **NOT** instances of:

    - :obj:`None`
    - :obj:`bool`
    - :obj:`bytes`
    - :obj:`ChainMap <collections.ChainMap>`
    - :obj:`Counter <collections.Counter>`
    - :obj:`OrderedDict <collections.OrderedDict>`
    - :obj:`UserDict <collections.UserDict>`
    - :obj:`UserString <collections.UserString>`
    - :obj:`defaultdict <collections.defaultdict>`
    - :obj:`Decimal <decimal.Decimal>`
    - :obj:`dict`
    - :obj:`float`
    - :obj:`int`
    - :obj:`str`
    - etc...

    Args:
        obj (Any): The object to be checked.

    Returns:
        bool: ``True`` if the given ``obj`` is list-like; ``False`` otherwise.

    Examples:
        >>> from flutils import is_list_like
        >>> is_list_like([1, 2, 3])
        True

        >>> is_list_like(reversed([1, 2, 4]))
        True

        >>> is_list_like('hello')
        False

        >>> is_list_like(sorted('hello'))
        True
    """
    if is_subclass_of_any(obj, *_LIST_LIKE):
        return True
    return False


def is_subclass_of_any(obj: _Any, *classes: _Any) -> bool:
    """Check if the given ``obj`` is a subclass of any of the given
    ``*classes``.

    Args:
        obj (Any): The object to check.
        *classes (Any): The classes to check against.

    Returns:
        bool: ``True`` if the given ``obj`` is an instance of ANY given
        ``*classes``; otherwise ``False``.

    Example:
        >>> from flutils import is_subclass_of_any
        >>> from collections import ValuesView, KeysView, UserList
        >>> obj = dict(a=1, b=2)
        >>> is_subclass_of_any(obj.keys(),ValuesView,KeysView,UserList)
        True
    """
    for cls in classes:
        if issubclass(obj.__class__, cls):
            return True
    return False
