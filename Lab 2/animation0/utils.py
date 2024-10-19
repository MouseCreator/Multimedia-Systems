
def last_index_of(lst, value):
    if value not in lst:
        return -1
    return len(lst) - 1 - lst[::-1].index(value)

def index_of(lst, value):
    return lst.index(value) if value in lst else -1