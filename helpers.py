from bunch import Bunch


def bbunchify(x):
    if isinstance(x, dict):
        return Bunch((k, bbunchify(v)) for k, v in x.items())
    elif isinstance(x, (list, tuple)):
        return type(x)(bbunchify(v) for v in x)
    else:
        return x
