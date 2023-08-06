
from .helpers import color_to_rgb565

__all__ = ['BaseDataPack',
           'DotDataPack',
           'LineDataPack',
           'RectangleDataPack',
           'CircleDataPack',
           'PictureDataPack',
           'IconDataPack',
           'AreaFillDataPack',
           'SpectrumDataPack',
           'SegmentDataPack',
           'ArcDataPack',
           'CharacterDataPack',
           'BicolorGraphDataPack',
           'BitmapDataPack',
           'DisplayZoomDataPack']


def _assign_ushort(value, name='value'):
    msg = '{} must be a unsigned short integer'.format(name)
    if type(value) is not int:
        raise TypeError(msg)
    if value < 0 or value >= 0x10000:
        raise ValueError(msg)
    return value


def _assign_coordinates(coords):
    msg = 'coordinates must be a 2-element tuple of unsigned short integers'
    if type(coords) is not tuple or len(coords) != 2:
        raise TypeError(msg)
    val = (_assign_ushort(coords[0], 'coordinates'),
           _assign_ushort(coords[1], 'coordinates'))
    return val


def _assign_colour(colour):
    msg = 'colour must be either a string or a unsigned short integer'
    if type(colour) is str:
        return color_to_rgb565(colour)
    return _assign_ushort(colour, 'colour')


def _assign_angle(value):
    if type(value) not in (int, float):
        raise TypeError('angle must be either an integer or a floating point value')
    if value < 0 or value > 360:
        raise ValueError('angle must be in range <0, 360>')
    return int(round(value * 2, 0))


class BaseDataPack(object):
    __slots__ = ()

    def __bytes__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()


class DotDataPack(BaseDataPack):
    """Data Pack for Dot graphic command."""

    __slots__ = ['_xy', '_colour']

    def __init__(self, xy, colour):
        self.xy = xy
        self.colour = colour

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    def __bytes__(self):
        return b''.join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big')])

    def __len__(self):
        return 6


class LineDataPack(BaseDataPack):
    """Data Pack for Line graphic command."""

    __slots__ = ['_colour', '_vertices']

    def __init__(self, colour, vertices):
        self.colour = colour
        self._vertices = []
        self += vertices

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    def __getitem__(self, key):
        return self._vertices.__getitem__(key)

    def __setitem__(self, key, value):
        if type(key) is int:
            tmp = _assign_coordinates(value)
        elif type(key) is slice:
            tmp = []
            for v in value:
                tmp.append(_assign_coordinates(v))
        else:
            raise TypeError('key must be either an integer or a slice')
        self._vertices.__setitem__(key, tmp)

    def __iadd__(self, other):
        msg = 'other must be a 2-element tuple of non-negative integers or a list of such objects'
        if type(other) is not list:
            other = [other]
        tmp = []
        for v in other:
            tmp.append(_assign_coordinates(v))
        self._vertices.extend(tmp)
        return self

    def __len__(self):
        return 2 + len(self._vertices) * 4

    def __bytes__(self):
        if len(self._vertices) < 2:
            raise RuntimeError('data pack must have at least 2 vertices')
        bb = bytearray()
        bb.extend(self._colour.to_bytes(2, 'big'))
        for v in self._vertices:
            for vv in v:
                bb.extend(vv.to_bytes(2, 'big'))
        return bytes(bb)


class RectangleDataPack(BaseDataPack):
    """Data Pack for Rectangle, Rectangle Area Fill and Rectangle XOR graphic commands."""

    __slots__ = '_xys', '_xye', '_colour'

    def __init__(self, xys, xye, colour):
        self.colour = colour
        if xys is None:
            self._xys = None
        else:
            self.xy_start = xys
        if xye is None:
            self._xye = None
        else:
            self.xy_end = xye

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    @property
    def xy_start(self):
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        self._xys = _assign_coordinates(value)

    @property
    def xy_end(self):
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        self._xye = _assign_coordinates(value)

    def __len__(self):
        return 10

    def __bytes__(self):
        if self._xys is None or self._xye is None:
            raise RuntimeError('all coordinates must be set')
        bb = bytearray().join([
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big')])
        return bytes(bb)


class CircleDataPack(BaseDataPack):
    """Data Pack for Circle graphic command."""

    __slots__ = '_xy', '_rad', '_colour'

    def __init__(self, xy, radius, colour):
        self.xy = xy
        self.radius = radius
        self.colour = colour

    def __len__(self):
        return 8

    def __bytes__(self):
        bb = bytearray().join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._rad.to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big')])
        return bytes(bb)

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def radius(self):
        return self._rad

    @radius.setter
    def radius(self, value):
        self._rad = _assign_ushort(value, 'radius')

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)


class PictureDataPack(BaseDataPack):
    """Data Pack for Picture Cut/Paste command."""

    __slots__ = '_picid', '_xys', '_xye', '_xy'

    def __init__(self, picid, xys, xye, xy):
        self.picid = picid
        self.xy_start = xys
        self.xy_end = xye
        self.xy = xy

    def __len__(self):
        return 14

    def __bytes__(self):
        return b''.join([
            self._picid.to_bytes(2, 'big'),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big')])

    @property
    def picid(self):
        """ID of the source image."""
        return self._picid

    @picid.setter
    def picid(self, value):
        self._picid = _assign_ushort(value, 'picid')

    @property
    def xy_start(self):
        """Top-left coordinates of the area being cut from the source image."""
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        self._xys = _assign_coordinates(value)

    @property
    def xy_end(self):
        """Bottom-right coordinates of the area being cut from the source image."""
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        self._xye = _assign_coordinates(value)

    @property
    def xy(self):
        """Position where to paste cut image, top-left coordinate."""
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)


class IconDataPack(BaseDataPack):
    """Data Pack for Icon Display command."""

    __slots__ = '_xy', '_iconid'

    def __init__(self, xy, iconid):
        self.xy = xy
        self.iconid = iconid

    def __len__(self):
        return 6

    def __bytes__(self):
        return b''.join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._iconid.to_bytes(2, 'big')])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def iconid(self):
        return self._iconid

    @iconid.setter
    def iconid(self, value):
        self._iconid = _assign_ushort(value, 'icon ID')


class AreaFillDataPack(BaseDataPack):
    """Data Pack for Area Fill command."""

    __slots__ = '_xy', '_colour'

    def __init__(self, xy, colour):
        self.xy = xy
        self.colour = colour

    def __len__(self):
        return 6

    def __bytes__(self):
        return b''.join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big')])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)


class SpectrumDataPack(BaseDataPack):
    """Data Pack for Spectrum command."""

    __slots__ = '_colour', '_x', '_ys', '_ye'

    def __init__(self, colour, x, ys, ye):
        self.colour = colour
        self.x = x
        self.y_start = ys
        self.y_end = ye

    def __len__(self):
        return 8

    def __bytes__(self):
        return b''.join([
            self._colour.to_bytes(2, 'big'),
            self._x.to_bytes(2, 'big'),
            self._ys.to_bytes(2, 'big'),
            self._ye.to_bytes(2, 'big')])

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = _assign_ushort(value, 'x')

    @property
    def y_start(self):
        return self._ys

    @y_start.setter
    def y_start(self, value):
        self._ys = _assign_ushort(value)

    @property
    def y_end(self):
        return self._ye

    @y_end.setter
    def y_end(self, value):
        self._ye = _assign_ushort(value)


class SegmentDataPack(BaseDataPack):
    """Data Pack for Segment command."""

    __slots__ = '_colour', '_xys', '_xye'

    def __init__(self, colour, xys, xye):
        self.colour = colour
        self.xy_start = xys
        self.xy_end = xye

    def __len__(self):
        return 10

    def __bytes__(self):
        return b''.join([
            self._colour.to_bytes(2, 'big'),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big')])

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    @property
    def xy_start(self):
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        self._xys = _assign_coordinates(value)

    @property
    def xy_end(self):
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        self._xye = _assign_coordinates(value)


class ArcDataPack(BaseDataPack):
    """Data Pack for Arc command."""

    __slots__ = '_colour', '_xy', '_rad', '_angles', '_anglee'

    def __init__(self, colour, xy, radius, angle_start, angle_end):
        self.colour = colour
        self.xy = xy
        self.radius = radius
        self.angle_start = angle_start
        self.angle_end = angle_end

    def __len__(self):
        return 12

    def __bytes__(self):
        return b''.join([
            self._colour.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._rad.to_bytes(2, 'big'),
            self._angles.to_bytes(2, 'big'),
            self._anglee.to_bytes(2, 'big')])

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def radius(self):
        return self._rad

    @radius.setter
    def radius(self, value):
        self._rad = _assign_ushort(value)

    @property
    def angle_start(self):
        return self._angles / 2

    @angle_start.setter
    def angle_start(self, value):
        self._angles = _assign_angle(value)

    @property
    def angle_end(self):
        return self._anglee / 2

    @angle_end.setter
    def angle_end(self, value):
        self._anglee = _assign_angle(value)


class CharacterDataPack(BaseDataPack):
    """Data Pack for Character command."""

    __slots__ = '_colour', '_xy', '_libid', '_encoding', '_sz', '_char'

    def __init__(self, colour, xy, libid, encoding, size, character):
        self.colour = colour
        self.xy = xy
        self.libid = libid
        self.encoding = encoding
        self.size = size
        self.character = character

    def __len__(self):
        return 12

    def __bytes__(self):
        if self._encoding[0] == 'unicode':
            char = ord(self._char).to_bytes(2, 'big')
        elif self._encoding[0] == '8bit':
            char = b''.join([b'\x00', self._char.encode('ascii')])
        else:
            char = self._char.encode(self._encoding[0])
            if len(char) == 1:
                char = b''.join([b'\x00', char])
            elif len(char) != 2:
                raise RuntimeError('encoded character does not fit in 2 bytes')

        return b''.join([
            self._colour.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._libid.to_bytes(1, 'big'),
            self._encoding[1].to_bytes(1, 'big'),
            self._sz[0].to_bytes(1, 'big'),
            self._sz[1].to_bytes(1, 'big'),
            char])

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = _assign_colour(value)

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def libid(self):
        return self._libid

    @libid.setter
    def libid(self, value):
        msg = 'library id must be a non-negative integer, less than 256'
        if type(value) is not int:
            raise TypeError(msg)
        if value < 0 or value >= 256:
            raise ValueError(msg)
        self._libid = value

    @property
    def encoding(self):
        return self._encoding[0]

    @encoding.setter
    def encoding(self, value):
        if type(value) not in [int, str]:
            raise TypeError('encoding must be either an integer (supported by the display) or a string name')

        encodings = enumerate(['8bit', 'gb2312', 'gbk', 'big5', 'sjis', 'unicode'])
        for idx, name in encodings:
            if ((type(value) is int and value == idx)
                    or (type(value) is str and value == name)):
                self._encoding = (name, idx)
                return
        if type(value) is int:
            raise ValueError('encoding not supported by the display (outside range <0, 5>)')
        self._encoding = (value, 0)

    @property
    def size(self):
        return self._sz

    @size.setter
    def size(self, value):
        msg = 'size must be a 2-element tuple of integers in range(256)'
        if (type(value) is not tuple
                or len(value) != 2
                or type(value[0]) is not int
                or type(value[1]) is not int):
            raise TypeError(msg)
        if value[0] not in range(256) or value[1] not in range(256):
            raise ValueError(msg)
        self._sz = value

    @property
    def character(self):
        return self._char

    @character.setter
    def character(self, value):
        if type(value) is int:
            self._char = chr(value)
        elif type(value) is str:
            if len(value) == 0:
                self._char = '\0'
            else:
                self._char = value[0]
        else:
            if self._encoding[0] == 'unicode':
                tmp = chr(int.from_bytes(value, 'big'))
            elif self._encoding[0] == '8bit':
                tmp = value.decode('ascii')
            else:
                tmp = value.decode(self._encoding[0])
            self._char = tmp[0]


class BicolorGraphDataPack(BaseDataPack):
    """Data Pack for Bicolorable Graph command."""

    __slots__ = '_xy', '_sz', '_colour', '_data'

    def __init__(self, xy, size, colour1, colour0, data=b''):
        self.xy = xy
        self.size = size
        self._colour = [0, 0]
        self.colour1 = colour1
        self.colour0 = colour0
        self._data = bytearray()
        self += data

    def __len__(self):
        return 12 + len(self._data)

    def __bytes__(self):
        bb = bytearray().join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._sz[0].to_bytes(2, 'big'),
            self._sz[1].to_bytes(2, 'big'),
            self._colour[0].to_bytes(2, 'big'),
            self._colour[1].to_bytes(2, 'big')])
        return b''.join([bb, self._data])

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        return self._data.__setitem__(key, value)

    def __iadd__(self, other):
        self._data += other
        return self

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def size(self):
        return self._sz

    @size.setter
    def size(self, value):
        self._sz = _assign_coordinates(value)

    @property
    def colour1(self):
        return self._colour[0]

    @colour1.setter
    def colour1(self, value):
        self._colour[0] = _assign_colour(value)

    @property
    def colour0(self):
        return self._colour[1]

    @colour0.setter
    def colour0(self, value):
        self._colour[1] = _assign_colour(value)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if type(value) not in (bytes, bytearray):
            raise TypeError('data must be a bytes-like object')
        self._data = bytearray(value)


class BitmapDataPack(BaseDataPack):
    """Data Pack for Bitmap command."""

    __slots__ = '_xy', '_sz', '_data'

    def __init__(self, xy, size, data=b''):
        self.xy = xy
        self.size = size
        self._data = bytearray()
        self += data

    def __len__(self):
        return 8 + len(self._data)

    def __bytes__(self):
        return b''.join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._sz[0].to_bytes(2, 'big'),
            self._sz[1].to_bytes(2, 'big'),
            self._data])

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __iadd__(self, other):
        self._data += other
        return self

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def size(self):
        return self._sz

    @size.setter
    def size(self, value):
        self._sz = _assign_coordinates(value)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if type(value) not in (bytes, bytearray):
            raise TypeError('data must be a bytes-like object')
        self._data = bytearray(value)


class DisplayZoomDataPack(BaseDataPack):
    """Data Pack for Display Zoom command."""

    __slots__ = '_xy', '_xys', '_xye'

    def __init__(self, xy, xys, xye):
        self.xy = xy
        self.xy_start = xys
        self.xy_end = xye

    def __len__(self):
        return 12

    def __bytes__(self):
        return b''.join([
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big')])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        self._xy = _assign_coordinates(value)

    @property
    def xy_start(self):
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        self._xys = _assign_coordinates(value)

    @property
    def xy_end(self):
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        self._xye = _assign_coordinates(value)
