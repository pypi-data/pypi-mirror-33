from collections import namedtuple


def siren_to_dict(o):
    return {
        attr: getattr(o, attr)
        for attr in dir(o)
        if attr[:1] != '_' and not callable(getattr(o, attr))
    }


def siren_to_entity(o):
    """
    Helper method that converts a siren entity into a namedtuple
    """
    attrs = siren_to_dict(o)
    return namedtuple(o.__class__.__name__, sorted(attrs))(**attrs)