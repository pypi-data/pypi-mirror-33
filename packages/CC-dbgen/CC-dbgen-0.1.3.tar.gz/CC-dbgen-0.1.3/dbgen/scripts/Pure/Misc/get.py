from typing import Any

import json
from dbgen.core.misc import cast_maybe

def get(dictstr: str
       ,key    : str
       ,dtype  : str
       ) -> Any:
    """
    Gets a key from a json'd dictionary
    """
    if not dictstr:  # catch cases of empty string and None
        return None

    assert dtype in cast_maybe.keys(), 'bad dtype argument for get: '+dtype

    try:
        d = json.loads(dictstr)
        out = d.get(key)

        return cast_maybe[dtype](out)
    except:
        print('failed to decode json in "GET"')
        import pdb;pdb.set_trace()
