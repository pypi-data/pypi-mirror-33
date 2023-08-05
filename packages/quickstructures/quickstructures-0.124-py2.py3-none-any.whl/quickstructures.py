
from collections import namedtuple as nt

def adict(**things):
    return things

def struct(**things):
    return nt('Struct', things.keys())(**things)

def nstruct(name):
    return struct(
        of = lambda **things: nt(name, things.keys())(**things)
    )

t = tuple
def tt(*things): return tuple(things)

