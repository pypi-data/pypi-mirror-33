import keyword
from collections import UserString
from typing import Union


_BUILTIN_NAMES = tuple(dir('__builtins__'))


def validate_identifier(
        identifier: Union[str, UserString],
        allow_underscore: bool = True
) -> None:
    """Validate the given string is a proper identifier.

    This validator will also raise an error if the given identifier is a
    keyword or a builtin identifier.

    Args:
         identifier (str): The value to be tested.
         allow_underscore (bool, optional): A value of ``False`` will raise
            an error when the ``identifier`` has a value that starts with an
            underscore ``_``.  (Use ``False`` when validating potential
            ``:obj:namedtuple`` keys)  Default: ``True``.
    Raises:
        SyntaxError: If the given identifier is invalid.
        TypeError: If the given identifier is not a :obj:`str`.
    """
    if isinstance(identifier, UserString):
        identifier = str(identifier)
    if not isinstance(identifier, str):
        raise TypeError(
            "The given 'identifier' must be a 'str'.  Got: %r"
            % type(identifier).__name__
        )
    identifier = identifier.strip()
    if not identifier:
        raise SyntaxError("The given 'identifier' cannot be empty")

    if allow_underscore is False and identifier[0:1] == '_':
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot start with an "
            "underscore '_'"
        )

    if identifier[0:1].isdigit():
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot start with a "
            "number"
        )

    if not identifier.isidentifier():
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, is invalid."
        )

    if keyword.iskeyword(identifier):
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot be a keyword"
        )

    if identifier in _BUILTIN_NAMES:
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot be a builtin name"
        )
    return None
