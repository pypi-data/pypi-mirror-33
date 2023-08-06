def build_params(param):
    params = {}
    for item in param:
        k, v = item.split('=', maxsplit=1)
        params[k] = v
    return params
