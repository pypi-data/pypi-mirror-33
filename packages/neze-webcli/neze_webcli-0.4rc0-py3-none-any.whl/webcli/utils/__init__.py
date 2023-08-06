def dict_update(d,s):
    if hasattr(s,'keys'):
        for k in s.keys():
            d[k] = dict_update(d.get(k,{}),s[k])
        return d
    return s
