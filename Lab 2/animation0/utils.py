
def last_index_of(lst, value):
    if value not in lst:
        return -1
    return len(lst) - 1 - lst[::-1].index(value)