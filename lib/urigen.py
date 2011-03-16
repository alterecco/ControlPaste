## http://code.activestate.com/recipes/576918/
## Short URL Generator

ALPHABET = 'YJedfRy8LNF2j6MrhkBSAQCX4DUP5amuH9vxVqbgpsGtnW7c3TwKE'
BLOCK_SIZE = 22

MASK = (1 << BLOCK_SIZE) - 1
MAPPING = range(BLOCK_SIZE)
MAPPING.reverse()

def encode_uri(n, min_length=0):
    return enbase(encode(n), min_length)
def encode(n):
    return (n & ~MASK) | _encode(n & MASK)
def _encode(n):
    result = 0
    for i, b in enumerate(MAPPING):
        if n & (1 << i):
            result |= (1 << b)
    return result
def enbase(x, min_length=0):
    result = _enbase(x)
    padding = ALPHABET[0] * (min_length - len(result))
    return '%s%s' % (padding, result)
def _enbase(x):
    n = len(ALPHABET)
    if x < n:
        return ALPHABET[x]
    return enbase(x/n) + ALPHABET[x%n]

def decode_uri(n):
    return decode(debase(n))

def decode(n):
    return (n & ~MASK) | _decode(n & MASK)
def _decode(n):
    result = 0
    for i, b in enumerate(MAPPING):
        if n & (1 << b):
            result |= (1 << i)
    return result
def debase(x):
    n = len(ALPHABET)
    result = 0
    for i, c in enumerate(reversed(x)):
        result += ALPHABET.index(c) * (n**i)
    return result
