from typing import Optional, Tuple
from re import finditer, MULTILINE, search, DOTALL


def parse_line(string: str, substr: str, index: int = 0
               ) -> Optional[str]:
    """
    Returns the n'th line containing substring
    Any negative index will return last one.
    """
    iter = finditer(substr + ".*$", string, MULTILINE)
    found = False

    for match in iter:
        if index == 0:
            return match[0]
        else:
            index -= 1
            found = True
    if found:
        return match[0]  # negative input for index
    else:
        return None


def btw(s: str, begin: str, end: str, off: int = 0
        ) -> Tuple[str, int]:
    result = search('%s(.*?)%s' % (begin, end), s[off:], DOTALL)
    if result:
        if result.group(1) is None:
            import pdb
            pdb.set_trace()
        return result.group(1), result.end() + off
    else:
        return '', 0
