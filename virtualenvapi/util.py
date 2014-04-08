
def split_package_name(p):
    """Splits the given package name and returns a tuple (name, ver)."""
    s = p.split('==')
    if len(s) == 1:
        return (s[0], None)
    else:
        return (s[0], s[1])
