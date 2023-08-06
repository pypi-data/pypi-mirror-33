
def reindent(s, numSpaces, prefix):
    _prefix = "\n"
    if prefix:
        _prefix+=prefix
    str = _prefix.join((numSpaces * " ") + i for i in s.splitlines())
    return str