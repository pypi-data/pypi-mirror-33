import dis

def to_int(x):
    if not isinstance(x, int):
        return ord(x)
    return x

def find_globals(co):
    globs = set()
    code = co.co_code
    n = len(code)
    i = 0
    extended_arg = 0
    while i < n:
        op = to_int(code[i])
        i = i+1
        if op >= dis.HAVE_ARGUMENT:
            oparg = to_int(code[i]) + to_int(code[i+1]) * 256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == dis.EXTENDED_ARG:
                extended_arg = oparg * 65536
            if op in dis.hasname and dis.opname[op].endswith("_GLOBAL"):
                globs.add(co.co_names[oparg])
    return globs

