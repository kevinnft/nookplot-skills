def find_substring(str1, sub_str):
    """Return True if sub_str appears in any string within str1, else False.

    The MBPP prompt expects `str1` to be an iterable of strings and `sub_str`
    to be the substring to search for.
    """
    return any(sub_str in s for s in str1)

