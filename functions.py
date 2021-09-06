
def coalesce(*args):
    for n, arg in enumerate(args):
        if n==len(args)-1:
            return arg
        if arg is not None: return arg
        else: continue