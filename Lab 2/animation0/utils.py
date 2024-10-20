
def last_index_of(lst, value):
    if value not in lst:
        return -1
    return len(lst) - 1 - lst[::-1].index(value)

def index_of(lst, value):
    return lst.index(value) if value in lst else -1

class IntPair:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __eq__(self, other):
        if isinstance(other, IntPair):
            return self.a == other.a and self.b == other.b
        return False

    def __hash__(self):
        return hash((self.a, self.b))

    def __repr__(self):
        return f"IntPair({self.a}, {self.b})"