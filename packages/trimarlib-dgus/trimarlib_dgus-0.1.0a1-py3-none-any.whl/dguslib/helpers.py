try:
    import webcolors
except ImportError:
    webcolors = None


def color_to_rgb565(name):
    if webcolors is None:
        raise RuntimeError('webcolors module not imported')
    tmp = webcolors.name_to_rgb(name)
    r = int((tmp[0] * 0x1F) / 0xFF)
    g = int((tmp[1] * 0x3F) / 0xFF)
    b = int((tmp[2] * 0x1F) / 0xFF)
    u16 = ((r & 0x1F) << 11) | ((g & 0x3F) << 5) | (b & 0x1F)
    return u16


def validate_int(value, range, name='value'):
    msg = '{} must be an integer in {}'.format(name, range)
    if type(value) is not int:
        raise TypeError(msg)
    if value not in range:
        raise ValueError(msg)


def validate_colour(value):
    if type(value) is str:
        return color_to_rgb565(value)
    validate_int(value, range(0x10000), 'colour')
    return value


def validate_int_tuple(value, count, range, name):
    msg = '{} must be a {}-element tuple of integers in {}'.format(name, count, range)
    if type(value) is not tuple:
        raise TypeError(msg)
    if len(value) != count:
        raise IndexError(msg)
    for idx, v in enumerate(value):
        validate_int(v, range, '{}[{}]'.format(name, idx))


def validate_bool(value, name):
    msg = '{} must be a boolean value'.format(name)
    if type(value) is not bool:
        raise TypeError(msg)


def validate_ushort(value, name):
    validate_int(value, range(0x10000), name)


def validate_ushort_tuple(value, count, name):
    validate_int_tuple(value, count, range(0x10000), name)


def validate_coordinates(value):
    validate_ushort_tuple(value, 2, 'coordinates')
