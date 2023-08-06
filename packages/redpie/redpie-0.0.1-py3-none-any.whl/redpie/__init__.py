"""
This modules allows you to use redis just like a Python dictionary
Example:

    from redpie import Redpie

    r = Redpie(db=0, host='localhost', port=6379)  # Or just r = Redpie(); 0, localhost and 6379 are defaults


    from requests import Session

    r.update({
        'you can': 'assign basic types',
        'and even more complex things': Session
    })

    >>> print(r['and even more complex things']())
    <requests.sessions.Session object at 0x10c68d5c0>
"""

from .redpie import Redpie
__version__ = "0.0.1"
