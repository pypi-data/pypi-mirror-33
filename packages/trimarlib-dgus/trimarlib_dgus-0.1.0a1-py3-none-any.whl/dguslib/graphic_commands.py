import enum
from . import data_packs

__all__ = ['DotCommand',
           'LineCommand',
           'RectangleCommand',
           'RectangleAreaFillCommand',
           'CircleCommand',
           'PicturePasteCommand',
           'IconDisplayCommand',
           'AreaFillCommand',
           'SpectrumCommand',
           'SegmentCommand',
           'ArcDisplayCommand',
           'CharacterCommand',
           'RectangleXorCommand',
           'BicolorGraphCommand',
           'BitmapCommand',
           'DisplayZoomCommand']


class BasicGraphicCommand(enum.IntEnum):
    dot = 1
    line = 2
    rectangle = 3
    rectangle_area_fill = 4
    circle = 5
    picture_cut_paste = 6
    icon_display = 7
    area_fill = 8
    spectrum = 9
    segment = 10
    arc_display = 11
    character = 12
    rectangle_xor = 13
    bicolor_graph = 14
    bitmap = 15
    paste_zoom = 16


class GraphicCommand(object):
    """Base class for specialized commands."""

    __slots__ = '_cmd', '_data_type', '_data'

    def __init__(self, cmd, data_type):
        self._cmd = BasicGraphicCommand(cmd)
        self._data_type = data_type
        self._data = []

    def __bytes__(self):
        bb = bytearray().join([self._cmd.to_bytes(2, 'big'),
                               len(self._data).to_bytes(2, 'big')])
        for d in self._data:
            bb.extend(bytes(d))
        return bytes(bb)

    def __iadd__(self, other):
        msg = 'other must be either of type {} or a iterable of such objects'.format(self._data_type)
        if type(other) is self._data_type:
            self._data.append(other)
        elif type(other) is not list:
            raise TypeError(msg)
        else:
            for d in other:
                if type(d) is not self._data_type:
                    raise TypeError(msg)
                self._data.append(d)
        return self

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        if type(value) is not self._data_type:
            raise TypeError('data type mismatch, expecting {}, got {}'.format(self._data_type, type(value)))
        return self._data.__setitem__(key, value)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        v = 4
        for d in self._data:
            v += len(d)
        return v

    def get_command(self):
        """Returns BasicGraphicCommand of the object."""
        return self._cmd

    @property
    def command(self):
        """Property wrapper around get_command method."""
        return self.get_command()

    @property
    def count(self):
        return len(self._data)


class DotCommand(GraphicCommand):
    """Sets single dot at specified coordinates to specified colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        """Initializes instance of the class.

        data_pack : either a single object of type DotDataPack or a
            iterable of such objects.
        """
        super().__init__(BasicGraphicCommand.dot, data_packs.DotDataPack)

        if data_pack is not None:
            self += data_pack


class LineCommand(GraphicCommand):
    """Draws a line in specified colour with specified vertices."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        """Initializes instance of the class.

        data_pack : either a single object of type LineDataPack or a
            iterable of such objects.
        """
        super().__init__(BasicGraphicCommand.line, data_packs.LineDataPack)

        if data_pack is not None:
            self += data_pack

    def __iadd__(self, other):
        if len(self._data) == 1:
            raise RuntimeError('Line command does not support multiple data packs')
        if type(other) is data_packs.LineDataPack:
            self._data.append(other)
            return self
        try:
            for d in other:
                if type(d) is not data_packs.LineDataPack:
                    raise TypeError()
                self += d
        except TypeError:
            raise TypeError('other must be either a single LineDataPack or a iterable of such objects')
        return self

    def __bytes__(self):
        bb = bytearray(self._cmd.to_bytes(2, 'big'))
        if len(self._data) == 0:
            bb.extend(bytes(2))
        else:
            cnt = len(self._data[0]._vertices) - 1
            dd = bytes(self._data[0])
            bb.extend(cnt.to_bytes(2, 'big'))
            bb.extend(dd)
        return bytes(bb)


class RectangleCommand(GraphicCommand):
    """Draws a rectangle within specified boundaries and in specified colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.rectangle, data_packs.RectangleDataPack)

        if data_pack is not None:
            self += data_pack


class RectangleAreaFillCommand(GraphicCommand):
    """Fills a rectangular area within specified boundaries with specified colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.rectangle_area_fill, data_packs.RectangleDataPack)

        if data_pack is not None:
            self += data_pack


class CircleCommand(GraphicCommand):
    """Draws a circle whose center, radius and colour are defined in CircleDataPack."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.circle, data_packs.CircleDataPack)

        if data_pack is not None:
            self += data_pack


class PicturePasteCommand(GraphicCommand):
    """Pastes part of another picture into current screen."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.picture_cut_paste, data_packs.PictureDataPack)

        if data_pack is not None:
            self += data_pack


class IconDisplayCommand(GraphicCommand):
    """Displays icon from specified library."""

    __slots__ = '_libid'

    def __init__(self, libid, data_pack=None):
        super().__init__(BasicGraphicCommand.icon_display, data_packs.IconDataPack)
        self.libid = libid

        if data_pack is not None:
            self += data_pack

    def __bytes__(self):
        bb = bytearray().join([
            self._libid.to_bytes(1, 'big'),
            self._cmd.to_bytes(1, 'big'),
            len(self._data).to_bytes(2, 'big')])
        for d in self._data:
            bb.extend(bytes(d))
        return bytes(bb)

    @property
    def libid(self):
        return self._libid

    @libid.setter
    def libid(self, value):
        msg = 'libid must be an integer in rage (256)'
        if type(value) is not int:
            raise TypeError(msg)
        if value not in range(256):
            raise ValueError(msg)
        self._libid = value


class AreaFillCommand(GraphicCommand):
    """Fills area with specified colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.area_fill, data_packs.AreaFillDataPack)

        if data_pack is not None:
            self += data_pack


class SpectrumCommand(GraphicCommand):
    """Draws vertical lines in specified colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.spectrum, data_packs.SpectrumDataPack)

        if data_pack is not None:
            self += data_pack


class SegmentCommand(GraphicCommand):
    """Connects points with colour."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.segment, data_packs.SegmentDataPack)

        if data_pack is not None:
            self += data_pack


class ArcDisplayCommand(GraphicCommand):
    """Draws an arc."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.arc_display, data_packs.ArcDataPack)

        if data_pack is not None:
            self += data_pack


class CharacterCommand(GraphicCommand):
    """Displays a single character."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.character, data_packs.CharacterDataPack)

        if data_pack is not None:
            self += data_pack


class RectangleXorCommand(GraphicCommand):
    """Inverts colour over specified rectangular area."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.rectangle_xor, data_packs.RectangleDataPack)

        if data_pack is not None:
            self += data_pack


class BicolorGraphCommand(GraphicCommand):
    """Displays a two-coloured bitmap in specified area."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.bicolor_graph, data_packs.BicolorGraphDataPack)

        if data_pack is not None:
            self += data_pack


class BitmapCommand(GraphicCommand):
    """Displays arbitrary bitmap with specified parameters, each pixel is in RGB565 format."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.bitmap, data_packs.BitmapDataPack)

        if data_pack is not None:
            self += data_pack


class DisplayZoomCommand(GraphicCommand):
    """Zooms specified area of the display."""

    __slots__ = ()

    def __init__(self, data_pack=None):
        super().__init__(BasicGraphicCommand.paste_zoom, data_packs.DisplayZoomDataPack)

        if data_pack is not None:
            self += data_pack
