import re


_CAMEL_TO_UNDERSCORE_RE = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel_to_underscore(
        text: str
) -> str:
    """Convert a camel-cased string to a string containing words separated
    with underscores.

    Args:
        text (str): The camel-cased string to convert.

    Returns:
        str: An underscore separated string.

    Example:
        >>> from flutils import camel_to_underscore
        >>> camel_to_underscore('FooBar')
        'foo_bar'
    """
    return _CAMEL_TO_UNDERSCORE_RE.sub(r'_\1', text).lower()


def underscore_to_camel(
        text: str,
        lower_first: bool = True
) -> str:
    """Convert a string with words separated by underscores to a camel-cased
    string.

    Args:
        text (str): The camel-cased string to convert.
        lower_first (bool, optional): Lowercase the first character.
            Defaults to ``True``
    Returns:
        str: A camel-cased string.

    Examples:
        >>> from flutils import underscore_to_camel
        >>> underscore_to_camel('foo_bar')
        'fooBar'

        >>> underscore_to_camel('_one__two___',lower_first=False)
        'OneTwo'
    """
    out = ''.join([x.capitalize() or '' for x in text.split('_')])
    if lower_first is True:
        return out[:1].lower() + out[1:]
    return out
