
from ..helpers import validate_int
from ..helpers import validate_bool
from ..helpers import validate_colour
from ..helpers import validate_int_tuple
from ..helpers import validate_ushort
from ..helpers import validate_ushort_tuple
from ..helpers import validate_coordinates


class VariableDescriptor(object):

    __slots__ = '_vp'

    def __init__(self, vp):
        self._vp = None
        self.vp = vp

    @property
    def vp(self):
        return self._vp

    @vp.setter
    def vp(self, value):
        validate_ushort(value, 'variable pointer')
        self._vp = value

    def __bytes__(self):
        raise NotImplementedError()


class VariableIconDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_v_range', '_icon_range', '_icon_lib', '_opaque'

    def __init__(self, vp, xy, v_range, icon_range, icon_lib, opaque):
        super().__init__(vp)
        self._xy = None
        self._v_range = None
        self._icon_range = None
        self._icon_lib = None
        self._opaque = None
        self.xy = xy
        self.v_range = v_range
        self.icon_range = icon_range
        self.icon_lib = icon_lib
        self.opaque = opaque

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def v_range(self):
        return self._v_range

    @v_range.setter
    def v_range(self, value):
        validate_ushort_tuple(value, 2, 'variable range')
        self._v_range = value

    @property
    def icon_range(self):
        return self._icon_range

    @icon_range.setter
    def icon_range(self, value):
        validate_ushort_tuple(value, 2, 'icon range')
        self._icon_range = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        msg = 'field must be a boolean value'
        if type(value) is not bool:
            raise TypeError(msg)
        self._opaque = value

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._v_range[0].to_bytes(2, 'big'),
            self._v_range[1].to_bytes(2, 'big'),
            self._icon_range[0].to_bytes(2, 'big'),
            self._icon_range[1].to_bytes(2, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big')
        ])


class AnimationIconDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_v_range', '_icon_stop', '_icon_range', '_icon_lib', '_opaque'

    def __init__(self, vp, xy, v_range, icon_stop, icon_range, icon_lib, opaque):
        super().__init__(vp)
        self._xy = None
        self._v_range = None
        self._icon_stop = None
        self._icon_range = None
        self._icon_lib = None
        self._opaque = None
        self.xy = xy
        self.v_range = v_range
        self.icon_stop = icon_stop
        self.icon_range = icon_range
        self.icon_lib = icon_lib
        self.opaque = opaque

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def v_range(self):
        return self._v_range

    @v_range.setter
    def v_range(self, value):
        validate_ushort_tuple(value, 2, 'variable range')
        self._v_range = value

    @property
    def v_stop(self):
        return self._v_range[0]

    @v_stop.setter
    def v_stop(self, value):
        self.v_range = (value, self._v_range[1])

    @property
    def v_start(self):
        return self._v_range[1]

    @v_start.setter
    def v_start(self, value):
        self.v_range = (self._v_range[0], value)

    @property
    def icon_stop(self):
        return self._icon_stop

    @icon_stop.setter
    def icon_stop(self, value):
        validate_ushort(value, 'icon stop id')
        self._icon_stop = value

    @property
    def icon_range(self):
        return self._icon_range

    @icon_range.setter
    def icon_range(self, value):
        validate_ushort_tuple(value, 2, 'icon range')
        self._icon_range = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        validate_bool(value, 'opaque')
        self._opaque = value

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            bytes(2),
            self._v_range[0].to_bytes(2, 'big'),
            self._v_range[1].to_bytes(2, 'big'),
            self._icon_stop.to_bytes(2, 'big'),
            self._icon_range[0].to_bytes(2, 'big'),
            self._icon_range[1].to_bytes(2, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big')])


class SliderDescriptor(VariableDescriptor):

    __slots__ = '_v_range', '_xy', '_icon_id', '_offset', '_horizontal', '_icon_lib', '_opaque', '_vp_mode'

    def __init__(self, vp, v_range, xy_range, icon_id, icon_lib, offset, horizontal, opaque, vp_mode):
        super(SliderDescriptor, self).__init__(vp)
        self._v_range = None
        self._xy = [0, 0, 0]
        self._icon_id = None
        self._offset = None
        self._icon_lib = None
        self._horizontal = None
        self._opaque = None
        self._vp_mode = None
        self.v_range = v_range
        self.xy = xy_range
        self.icon_id = icon_id
        self.icon_lib = icon_lib
        self.offset = offset
        self.horizontal = horizontal
        self.opaque = opaque
        self.vp_mode = vp_mode

    @property
    def v_range(self):
        return self._v_range

    @v_range.setter
    def v_range(self, value):
        validate_ushort_tuple(value, 2, 'variable range')
        self._v_range = value

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def icon_id(self):
        return self._icon_id

    @icon_id.setter
    def icon_id(self, value):
        validate_ushort(value, 'icon id')
        self._icon_id = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        validate_int(value, range(256), 'offset')
        self._offset = value

    @property
    def horizontal(self):
        return self._horizontal

    @horizontal.setter
    def horizontal(self, value):
        validate_bool(value, 'property')
        self._horizontal = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        validate_bool(value, 'property')
        self._opaque = value

    @property
    def vp_mode(self):
        return self._vp_mode

    @vp_mode.setter
    def vp_mode(self, value):
        validate_int(value, range(3), 'variable mode')
        self._vp_mode = value

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._v_range[0].to_bytes(2, 'big'),
            self._v_range[1].to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._icon_id.to_bytes(2, 'big'),
            self._xy[2].to_bytes(2, 'big'),
            self._offset.to_bytes(1, 'big'),
            self._horizontal.to_bytes(1, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big'),
            self._vp_mode.to_bytes(1, 'big'),
            bytes(1)
        ])


class WordArtDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_icon0', '_icon_lib', '_opaque', '_decimal_format', '_var_mode', '_alignment'

    def __init__(self, vp, xy, icon0, icon_lib, opaque, decimal_format, mode, alignment):
        super().__init__(vp)
        self._xy = None
        self._icon0 = None
        self._icon_lib = None
        self._opaque = None
        self._decimal_format = None
        self._var_mode = None
        self._alignment = None
        self.xy = xy
        self.icon0 = icon0
        self.icon_lib = icon_lib
        self.opaque = opaque
        self.decimal_format = decimal_format
        self.mode = mode
        self.alignment = alignment

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._icon0.to_bytes(2, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big'),
            self._decimal_format[0].to_bytes(1, 'big'),
            self._decimal_format[1].to_bytes(1, 'big'),
            self._var_mode.to_bytes(1, 'big'),
            self._alignment[0].to_bytes(1, 'big')
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def icon0(self):
        return self._icon0

    @icon0.setter
    def icon0(self, value):
        validate_ushort(value, 'first icon index')
        self._icon0 = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        validate_bool(value, 'opaque')
        self._opaque = value

    @property
    def decimal_format(self):
        return self._decimal_format

    @decimal_format.setter
    def decimal_format(self, value):
        validate_int_tuple(value, 2, range(256), 'decimal format')
        self._decimal_format = value

    @property
    def mode(self):
        return self._var_mode

    @mode.setter
    def mode(self, value):
        validate_int(value, range(7), 'variable mode')
        self._var_mode = value

    @property
    def alignment(self):
        return self._alignment[1]

    @alignment.setter
    def alignment(self, value):
        msg = 'alignment must be either a string or an integer'
        if type(value) not in (str, int):
            raise TypeError(msg)
        for idx, name in [(0, 'left'), (1, 'right')]:
            if (type(value) is str and value == name) or (type(value) is int and value == idx):
                self._alignment = idx, name
                return
        raise ValueError('invalid alignment')


class ImageAnimationDescriptor(VariableDescriptor):

    __slots__ = '_pic_range', '_frame_time'

    def __init__(self, pic_range, frame_time):
        super().__init__(0)
        self._pic_range = None
        self._frame_time = None
        self.picture_range = pic_range
        self.frame_time = frame_time

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._pic_range[0].to_bytes(2, 'big'),
            self._pic_range[1].to_bytes(2, 'big'),
            self._frame_time.to_bytes(1, 'big')
        ])

    @property
    def picture_range(self):
        return self._pic_range

    @picture_range.setter
    def picture_range(self, value):
        validate_ushort_tuple(value, 2, 'picture range')
        self._pic_range = value

    @property
    def picture_begin(self):
        return self._pic_range[0]

    @picture_begin.setter
    def picture_begin(self, value):
        self.picture_range = (value, self._pic_range[1])

    @property
    def picture_end(self):
        return self._pic_range[1]

    @picture_end.setter
    def picture_end(self, value):
        self.picture_range = (self._pic_range[0], value)

    @property
    def frame_time(self):
        return self._frame_time * 8

    @frame_time.setter
    def frame_time(self, value):
        validate_int(value, range(256 * 8), 'frame time')
        self._frame_time = int(value / 8)


class IconRotationDescriptor(VariableDescriptor):

    __slots__ = ('_icon_id', '_icon_center', '_xy_center', '_var_range', '_angle_range', '_var_mode', '_icon_lib',
                 '_opaque')

    def __init__(self, vp, icon_id, icon_center, xy_center, var_range, angle_range, mode, icon_lib, opaque):
        super().__init__(vp)
        self._icon_id = None
        self._icon_center = None
        self._xy_center = None
        self._var_range = None
        self._angle_range = None
        self._var_mode = None
        self._icon_lib = None
        self._opaque = None
        self.icon_id = icon_id
        self.icon_lib = icon_lib
        self.icon_center = icon_center
        self.xy_center = xy_center
        self.variable_range = var_range
        self.angle_range = angle_range
        self.mode = mode
        self.opaque = opaque

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._icon_id.to_bytes(2, 'big'),
            self._icon_center[0].to_bytes(2, 'big'),
            self._icon_center[1].to_bytes(2, 'big'),
            self._xy_center[0].to_bytes(2, 'big'),
            self._xy_center[1].to_bytes(2, 'big'),
            self._var_range[0].to_bytes(2, 'big'),
            self._var_range[1].to_bytes(2, 'big'),
            self._angle_range[0].to_bytes(2, 'big'),
            self._angle_range[1].to_bytes(2, 'big'),
            self._var_mode.to_bytes(1, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big')
        ])

    @property
    def icon_id(self):
        return self._icon_id

    @icon_id.setter
    def icon_id(self, value):
        validate_ushort(value, 'icon id')
        self._icon_id = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def icon_center(self):
        return self._icon_center

    @icon_center.setter
    def icon_center(self, value):
        validate_coordinates(value)
        self._icon_center = value

    @property
    def xy_center(self):
        return self._xy_center

    @xy_center.setter
    def xy_center(self, value):
        validate_coordinates(value)
        self._xy_center = value

    @property
    def variable_range(self):
        return self._var_range

    @variable_range.setter
    def variable_range(self, value):
        validate_ushort_tuple(value, 2, 'variable range')
        self._var_range = value

    @property
    def variable_min(self):
        return self._var_range[0]

    @variable_min.setter
    def variable_min(self, value):
        self.variable_range = (value, self._var_range[1])

    @property
    def variable_max(self):
        return self._var_range[1]

    @variable_max.setter
    def variable_max(self, value):
        self.variable_range = (self._var_range[0], value)

    @property
    def angle_range(self):
        return self._angle_range

    @angle_range.setter
    def angle_range(self, value):
        msg = 'angle range must be a 2-element tuple of numeric values in range <0, 360>'
        if type(value) is not tuple:
            raise TypeError(msg)
        if len(value) != 2:
            raise IndexError(msg)
        vv = []
        for v in value:
            if v < 0 or v > 360:
                raise ValueError(msg)
            vv.append(int(round(v * 2, 0)))
        self._angle_range = tuple(vv)

    @property
    def angle_min(self):
        return self._angle_range[0]

    @angle_min.setter
    def angle_min(self, value):
        self.angle_range = (value, self._angle_range[1])

    @property
    def angle_max(self):
        return self._angle_range[1]

    @angle_max.setter
    def angle_max(self, value):
        self.angle_range = (self._angle_range[0], value)

    @property
    def mode(self):
        return self._var_mode

    @mode.setter
    def mode(self, value):
        validate_int(value, range(3), 'variable mode')
        self._var_mode = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        validate_bool(value, 'opaque')
        self._opaque = value


class BitVariableDescriptor(VariableDescriptor):

    __slots__ = ('_vp_aux', '_bit_mask', '_display_mode', '_arrangement', '_opaque', '_icon_lib', '_icon0_range',
                 '_icon1_range', '_xy', '_spacing')

    def __init__(self, vp, vp_aux, xy, bit_mask, display_mode, arrangement, opaque, icon_lib, icon0_range, icon1_range,
                 spacing):
        super().__init__(vp)
        self._vp_aux = None
        self.vp_aux = vp_aux
        self._bit_mask = None
        self.bit_mask = bit_mask
        self._display_mode = None
        self.display_mode = display_mode
        self._arrangement = None
        self.arrangement = arrangement
        self._opaque = None
        self.opaque = opaque
        self._icon_lib = None
        self.icon_lib = icon_lib
        self._icon0_range = None
        self.icon0_range = icon0_range
        self._icon1_range = None
        self.icon1_range = icon1_range
        self._spacing = None
        self.spacing = spacing
        self._xy = None
        self.xy = xy

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._vp_aux.to_bytes(2, 'big'),
            self._bit_mask.to_bytes(2, 'big'),
            self._display_mode.to_bytes(1, 'big'),
            self._arrangement.to_bytes(1, 'big'),
            self._opaque.to_bytes(1, 'big'),
            self._icon_lib.to_bytes(1, 'big'),
            self._icon0_range[0].to_bytes(2, 'big'),
            self._icon0_range[1].to_bytes(2, 'big'),
            self._icon1_range[0].to_bytes(2, 'big'),
            self._icon1_range[1].to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._spacing.to_bytes(2, 'big')
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def vp_aux(self):
        return self._vp_aux

    @vp_aux.setter
    def vp_aux(self, value):
        validate_int(value, range(0x7000), 'vp aux')
        self._vp_aux = value

    @property
    def bit_mask(self):
        return self._bit_mask

    @bit_mask.setter
    def bit_mask(self, value):
        validate_ushort(value, 'bit mask')
        self._bit_mask = value

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        validate_int(value, range(8), 'display mode')
        self._display_mode = value

    @property
    def arrangement(self):
        return self._arrangement

    @arrangement.setter
    def arrangement(self, value):
        validate_int(value, range(4), 'arrangement')
        self._arrangement = value

    @property
    def opaque(self):
        return self._opaque

    @opaque.setter
    def opaque(self, value):
        validate_bool(value, 'opaque')
        self._opaque = value

    @property
    def icon_lib(self):
        return self._icon_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icon_lib = value

    @property
    def icon0_range(self):
        return self._icon0_range

    @icon0_range.setter
    def icon0_range(self, value):
        validate_ushort_tuple(value, 2, 'icon0 range')
        self._icon0_range = value

    @property
    def icon1_range(self):
        return self._icon1_range

    @icon1_range.setter
    def icon1_range(self, value):
        validate_ushort_tuple(value, 2, 'icon1 range')
        self._icon1_range = value

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        validate_ushort(value, 'icon spacing')
        self._spacing = value


class DataVariableDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_colour', '_lib_id', '_font_x_size', '_alignment', '_decimal_format', '_var_mode', '_unit'

    def __init__(self, vp, xy, colour, lib_id, font_x_size, alignment, decimal_format, mode, unit):
        super().__init__(vp)
        self._xy = None
        self._colour = None
        self._lib_id = None
        self._font_x_size = None
        self._alignment = None
        self._decimal_format = None
        self._var_mode = None
        self._unit = None
        self.xy = xy
        self.colour = colour
        self.lib_id = lib_id
        self.font_x_size = font_x_size
        self.alignment = alignment
        self.decimal_format = decimal_format
        self.mode = mode
        self.unit = unit

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big'),
            self._lib_id.to_bytes(1, 'big'),
            self._font_x_size.to_bytes(1, 'big'),
            self._alignment[0].to_bytes(1, 'big'),
            self._decimal_format[0].to_bytes(1, 'big'),
            self._decimal_format[1].to_bytes(1, 'big'),
            self._var_mode.to_bytes(1, 'big'),
            len(self._unit).to_bytes(1, 'big'),
            self._unit,
            bytes(11 - len(self._unit))
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        v = validate_colour(value)
        self._colour = v

    @property
    def lib_id(self):
        return self._lib_id

    @lib_id.setter
    def lib_id(self, value):
        validate_int(value, range(256), 'library id')
        self._lib_id = value

    @property
    def font_x_size(self):
        return self._font_x_size

    @font_x_size.setter
    def font_x_size(self, value):
        validate_int(value, range(128), 'font x size')
        self._font_x_size = value

    @property
    def alignment(self):
        return self._alignment[1]

    @alignment.setter
    def alignment(self, value):
        msg = 'alignment must be either a string or an integer'
        if type(value) not in (str, int):
            raise TypeError(msg)
        for idx, name in enumerate(['right', 'left', 'center']):
            if (type(value) is int and value == idx) or (type(value) is str and value == name):
                self._alignment = idx, name
                return
        raise ValueError('invalid alignment')

    @property
    def decimal_format(self):
        return self._decimal_format

    @decimal_format.setter
    def decimal_format(self, value):
        validate_int_tuple(value, 2, range(20), 'decimal format')
        if value[0] + value[1] >= 20:
            raise ValueError('sum of integer and decimal digits must be less than 20')
        self._decimal_format = value

    @property
    def mode(self):
        return self._var_mode

    @mode.setter
    def mode(self, value):
        validate_int(value, range(7), 'variable mode')
        self._var_mode = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        msg = 'unit must be either a string or a bytes-like object of 11 characters at most'
        if type(value) not in (str, bytes, bytearray):
            raise TypeError(msg)
        if len(value) > 11:
            raise IndexError(msg)
        if type(value) is str:
            self._unit = value.encode('ascii')
        else:
            self._unit = value


class TextDescriptor(VariableDescriptor):

    __slots__ = ('_xy', '_colour', '_area', '_text_length', '_font_id', '_font_size', '_encoding', '_spacing',
                 '_fixed_spacing')

    def __init__(self, vp, xy, colour, area, text_length, font_id, font_size, encoding, spacing, fixed_spacing=False):
        super().__init__(vp)
        self._xy = None
        self._colour = None
        self._area = None
        self._text_length = None
        self._font_id = None
        self._font_size = None
        self._encoding = None
        self._spacing = None
        self._fixed_spacing = None
        self.xy = xy
        self.colour = colour
        self.area = area
        self.text_length = text_length
        self.font_id = font_id
        self.font_size = font_size
        self.encoding = encoding
        self.spacing = spacing
        self.fixed_spacing = fixed_spacing

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big'),
            self._area[0][0].to_bytes(2, 'big'),
            self._area[0][1].to_bytes(2, 'big'),
            self._area[1][0].to_bytes(2, 'big'),
            self._area[1][1].to_bytes(2, 'big'),
            self._text_length.to_bytes(2, 'big'),
            self._font_id[0].to_bytes(1, 'big'),
            self._font_id[1].to_bytes(1, 'big'),
            self._font_size[0].to_bytes(1, 'big'),
            self._font_size[1].to_bytes(1, 'big'),
            (self._encoding[0] | (0x80 if self._fixed_spacing else 0)).to_bytes(1, 'big'),
            self._spacing[0].to_bytes(1, 'big'),
            self._spacing[1].to_bytes(1, 'big'),
            bytes(1)
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        v = validate_colour(value)
        self._colour = v

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        msg = 'area must be 2-element tuple of coordinates'
        if type(value) is not tuple:
            raise TypeError(msg)
        if len(value) != 2:
            raise IndexError(msg)
        for v in value:
            validate_coordinates(v)
        self._area = value

    @property
    def xy_start(self):
        return self._area[0]

    @xy_start.setter
    def xy_start(self, value):
        self.area = (value, self._area[1])

    @property
    def xy_end(self):
        return self._area[1]

    @xy_end.setter
    def xy_end(self, value):
        self.area = (self._area[1], value)

    @property
    def text_length(self):
        return self._text_length

    @text_length.setter
    def text_length(self, value):
        validate_ushort(value, 'text length')
        self._text_length = value

    @property
    def font_id(self):
        return self._font_id

    @font_id.setter
    def font_id(self, value):
        validate_int_tuple(value, 2, range(256), 'font id')
        self._font_id = value

    @property
    def font0_id(self):
        return self._font_id[0]

    @font0_id.setter
    def font0_id(self, value):
        self.font_id = (value, self._font_id[1])

    @property
    def font1_id(self):
        return self._font_id[1]

    @font1_id.setter
    def font1_id(self, value):
        self.font_id = (self._font_id[0], value)

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        validate_int_tuple(value, 2, range(256), 'font size')
        self._font_size = value

    @property
    def font_x_size(self):
        return self._font_size[0]

    @font_x_size.setter
    def font_x_size(self, value):
        self.font_size = (value, self._font_size[1])

    @property
    def font_y_size(self):
        return self._font_size[1]

    @font_y_size.setter
    def font_y_size(self, value):
        self.font_size = (self._font_size[0], value)

    @property
    def encoding(self):
        return self._encoding[1]

    @encoding.setter
    def encoding(self, value):
        msg = 'encoding must be either an integer or a string'
        if type(value) not in (int, str):
            raise TypeError(msg)
        for idx, name in enumerate(['8bit', 'gb2312', 'gbk', 'big5', 'sjis', 'unicode']):
            if (type(value) is int and value == idx) or (type(value) is str and value == name):
                self._encoding = idx, name
                return
        if type(value) is int:
            raise ValueError('encoding number out of range(6)')
        self._encoding = 0, value

    @property
    def fixed_spacing(self):
        return self._fixed_spacing

    @fixed_spacing.setter
    def fixed_spacing(self, value):
        validate_bool(value, 'fixed spacing')
        self._fixed_spacing = value

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        validate_int_tuple(value, 2, range(256), 'spacing')
        self._spacing = value

    @property
    def spacing_horizontal(self):
        return self._spacing[0]

    @spacing_horizontal.setter
    def spacing_horizontal(self, value):
        self.spacing = (value, self._spacing[1])

    @property
    def spacing_vertical(self):
        return self._spacing[1]

    @spacing_vertical.setter
    def spacing_vertical(self, value):
        self.spacing = (self._spacing[0], value)


class DigitalRTCDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_colour', '_lib_id', '_font_x_size', '_string_code'

    def __init__(self, xy, colour, lib_id, font_x_size, string_code):
        super().__init__(0)
        self._xy = None
        self._colour = None
        self._lib_id = None
        self._font_x_size = None
        self._string_code = None
        self.xy = xy
        self.colour = colour
        self.lib_id = lib_id
        self.font_x_size = font_x_size
        self.string_code = string_code

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big'),
            self._lib_id.to_bytes(1, 'big'),
            self._font_x_size.to_bytes(1, 'big'),
            self._string_code,
            bytes(16 - len(self._string_code))
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        v = validate_colour(value)
        self._colour = v

    @property
    def lib_id(self):
        return self._lib_id

    @lib_id.setter
    def lib_id(self, value):
        validate_int(value, range(256), 'library id')
        self._lib_id = value

    @property
    def font_x_size(self):
        return self._font_x_size

    @font_x_size.setter
    def font_x_size(self, value):
        validate_int(value, range(128), 'font x size')
        self._font_x_size = value

    @property
    def string_code(self):
        return self._string_code

    @string_code.setter
    def string_code(self, value):
        msg = 'string code must be a string or bytes-like object of 16 characters at most'
        if type(value) not in (str, bytes, bytearray):
            raise TypeError(msg)
        if len(value) > 16:
            raise IndexError(msg)
        if type(value) is str:
            self._string_code = value.encode('ascii')
        else:
            self._string_code = value


class AnalogRTCDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_icons', '_icons_centers', '_icons_lib'

    def __init__(self, xy, icons, icon_centers, icon_lib):
        super().__init__(1)
        self._xy = None
        self._icons = None
        self._icons_centers = None
        self._icons_lib = None
        self.xy = xy
        self.icons = icons
        self.icon_centers = icon_centers
        self.icon_lib = icon_lib

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._icons[0].to_bytes(2, 'big'),
            self._icons_centers[0][0].to_bytes(2, 'big'),
            self._icons_centers[0][1].to_bytes(2, 'big'),
            self._icons[1].to_bytes(2, 'big'),
            self._icons_centers[1][0].to_bytes(2, 'big'),
            self._icons_centers[1][1].to_bytes(2, 'big'),
            self._icons[2].to_bytes(2, 'big'),
            self._icons_centers[2][0].to_bytes(2, 'big'),
            self._icons_centers[2][1].to_bytes(2, 'big'),
            self._icons_lib.to_bytes(1, 'big'),
            bytes(1)
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def icons(self):
        return self._icons

    @icons.setter
    def icons(self, value):
        validate_ushort_tuple(value, 3, 'icons')
        self._icons = value

    @property
    def icon_hours(self):
        return self._icons[0]

    @icon_hours.setter
    def icon_hours(self, value):
        validate_ushort(value, 'hours icon')
        self._icons = (value, self._icons[1], self._icons[2])

    @property
    def icon_minutes(self):
        return self._icons[1]

    @icon_minutes.setter
    def icon_minutes(self, value):
        validate_ushort(value, 'minutes icon')
        self._icons = (self._icons[0], value, self._icons[2])

    @property
    def icon_seconds(self):
        return self._icons[2]

    @icon_seconds.setter
    def icon_seconds(self, value):
        validate_ushort(value, 'seconds icon')
        self._icons = (self._icons[0], self._icons[1], value)

    @property
    def icon_centers(self):
        return self._icons_centers

    @icon_centers.setter
    def icon_centers(self, value):
        msg = 'icon centers must be a 3-element tuple of coordinates'
        if type(value) is not tuple:
            raise TypeError(msg)
        if len(value) != 3:
            raise IndexError(msg)
        for v in value:
            validate_coordinates(v)
        self._icons_centers = value

    @property
    def icon_hours_center(self):
        return self._icons_centers[0]

    @icon_hours_center.setter
    def icon_hours_center(self, value):
        self.icon_centers = (value, self._icons_centers[1], self._icons_centers[2])

    @property
    def icon_minutes_center(self):
        return self._icons_centers[1]

    @icon_minutes_center.setter
    def icon_minutes_center(self, value):
        self.icon_centers = (self._icons_centers[0], value, self._icons_centers[2])

    @property
    def icon_seconds_center(self):
        return self._icons_centers[2]

    @icon_seconds_center.setter
    def icon_seconds_center(self, value):
        self.icon_centers = (self._icons_centers[0], self._icons_centers[1], value)

    @property
    def icon_lib(self):
        return self._icons_lib

    @icon_lib.setter
    def icon_lib(self, value):
        validate_int(value, range(256), 'icon library')
        self._icons_lib = value


class HexVariableDescriptor(VariableDescriptor):

    __slots__ = '_xy', '_colour', '_bytes_count', '_lib_id', '_font_x_size', '_separators'

    def __init__(self, vp, xy, colour, bytes_count, lib_id, font_x_size, separators):
        super().__init__(vp)
        self._xy = None
        self.xy = xy
        self._colour = None
        self.colour = colour
        self._bytes_count = None
        self.bytes_count = bytes_count
        self._lib_id = None
        self.lib_id = lib_id
        self._font_x_size = None
        self.font_x_size = font_x_size
        self._separators = None
        self.separators = separators

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xy[0].to_bytes(2, 'big'),
            self._xy[1].to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big'),
            self._bytes_count.to_bytes(1, 'big'),
            self._lib_id.to_bytes(1, 'big'),
            self._font_x_size.to_bytes(1, 'big'),
            self._separators,
            bytes(15 - len(self._separators))
        ])

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        validate_coordinates(value)
        self._xy = value

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        v = validate_colour(value)
        self._colour = v

    @property
    def bytes_count(self):
        return self._bytes_count

    @bytes_count.setter
    def bytes_count(self, value):
        validate_int(value, range(1, 16), 'bytes count')
        self._bytes_count = value

    @property
    def lib_id(self):
        return self._lib_id

    @lib_id.setter
    def lib_id(self, value):
        validate_int(value, range(256), 'library id')
        self._lib_id = value

    @property
    def font_x_size(self):
        return self._font_x_size

    @font_x_size.setter
    def font_x_size(self, value):
        validate_int(value, range(128), 'font x size')
        self._font_x_size = value

    @property
    def separators(self):
        return self._separators

    @separators.setter
    def separators(self, value):
        msg = 'separators must be a string or a bytes-like object of 15 characters at most'
        if type(value) not in (str, bytes, bytearray):
            raise TypeError(msg)
        if len(value) > 15:
            raise IndexError(msg)
        if type(value) is str:
            self._separators = value.encode('ascii')
        else:
            self._separators = value


class DynamicTrendCurveDescriptor(VariableDescriptor):

    __slots__ = '_xys', '_xye', '_center_y', '_center_var', '_colour', '_mul_y', '_channel', '_spacing'

    def __init__(self, xy_top_left, xy_bottom_right, center_y, center_value, colour, mul_y, channel, spacing):
        super().__init__(0)
        self._xys = None
        self.xy_start = xy_top_left
        self._xye = None
        self.xy_end = xy_bottom_right
        self._center_y = None
        self.center_y = center_y
        self._center_var = None
        self.center_value = center_value
        self._colour = None
        self.colour = colour
        self._mul_y = None
        self.mul_y = mul_y
        self._channel = None
        self.channel = channel
        self._spacing = None
        self.spacing = spacing

    def __bytes__(self):
        return b''.join([
            bytes(2),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big'),
            self._center_y.to_bytes(2, 'big'),
            self._center_var.to_bytes(2, 'big'),
            self._colour.to_bytes(2, 'big'),
            self._mul_y.to_bytes(2, 'big'),
            self._channel.to_bytes(1, 'big'),
            self._spacing.to_bytes(1, 'big')
        ])

    @property
    def xy_start(self):
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        validate_coordinates(value)
        self._xys = value

    @property
    def xy_end(self):
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        validate_coordinates(value)
        self._xye = value

    @property
    def center_y(self):
        return self._center_y

    @center_y.setter
    def center_y(self, value):
        validate_ushort(value, 'center y coordinate')
        self._center_y = value

    @property
    def center_value(self):
        return self._center_var

    @center_value.setter
    def center_value(self, value):
        validate_ushort(value, 'center value')
        self._center_var = value

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        v = validate_colour(value)
        self._colour = v

    @property
    def mul_y(self):
        return self._mul_y

    @mul_y.setter
    def mul_y(self, value):
        validate_int(value, range(0x8000), 'multiplication y')
        self._mul_y = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        validate_int(value, range(8), 'channel')
        self._channel = value

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        validate_int(value, range(1, 256), 'spacing')
        self._spacing = value


class BasicGraphicsDescriptor(VariableDescriptor):

    __slots__ = '_xys', '_xye', '_dashed_line', '_dashed_pattern'

    def __init__(self, vp, xy_top_left, xy_bottom_right, dashed_line, dashed_pattern):
        super().__init__(vp)
        self._xys = None
        self._xye = None
        self._dashed_line = None
        self._dashed_pattern = None
        self.area = (xy_top_left, xy_bottom_right)
        self.dashed_line = dashed_line
        self.dashed_pattern = dashed_pattern

    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big'),
            b'\x5A' if self._dashed_line else b'\x00',
            self._dashed_pattern,
            bytes(13)
        ])

    @property
    def xy_start(self):
        return self._xys

    @xy_start.setter
    def xy_start(self, value):
        validate_coordinates(value)
        self._xys = value

    @property
    def xy_end(self):
        return self._xye

    @xy_end.setter
    def xy_end(self, value):
        validate_coordinates(value)
        self._xye = value

    @property
    def area(self):
        return self._xys, self._xye

    @area.setter
    def area(self, value):
        msg = 'area must be a 2-element tuple of coordinates'
        if type(value) is not tuple:
            raise TypeError(msg)
        if len(value) != 2:
            raise IndexError(msg)
        for v in value:
            validate_coordinates(v)
        self._xys, self._xye = value

    @property
    def dashed_line(self):
        return self._dashed_line

    @dashed_line.setter
    def dashed_line(self, value):
        validate_bool(value, 'dashed line flag')

    @property
    def dashed_pattern(self):
        return self._dashed_pattern

    @dashed_pattern.setter
    def dashed_pattern(self, value):
        msg = 'dashed pattern must be either None or a bytes-like object of 4 elements'
        if value is None:
            self._dashed_pattern = bytes(4)
            return
        if type(value) not in (bytes, bytearray):
            raise TypeError(msg)
        if len(value) != 4:
            raise IndexError(msg)
        self._dashed_pattern = value


class TableDescriptor(VariableDescriptor):

    __slots__ = ('_tab_size', '_tab_offset', '_data_size', '_encoding', '_xys', '_xye', '_colour_line', '_colour_text',
                 '_font_id', '_font_size', '_hide_col_head', '_hide_row_head')
    
    def __init__(self, vp, table_size, table_offset, data_size, encoding, xy_start, xy_end, colour_line, colour_text,
                 font_id, font_size, hide_col_header, hide_row_header):
        super().__init__(vp)
        self._tab_size = None
        self._tab_offset = None
        self._data_size = None
        self._encoding = None
        self._xys = None
        self._xye = None
        self._colour_line = None
        self._colour_text = None
        self._font_id = None
        self._font_size = None
        self._hide_col_head = None
        self._hide_row_head = None
        self.table_size = table_size
        self.table_offset = table_offset
        self.data_size = data_size
        self.encoding = encoding
        self.xy_start = xy_start
        self.xy_end = xy_end
        self.colour_line = colour_line
        self.colour_text = colour_text
        self.font_id = font_id
        self.font_size = font_size
        self.hide_col_header = hide_col_header
        self.hide_row_header = hide_row_header
    
    def __bytes__(self):
        return b''.join([
            self._vp.to_bytes(2, 'big'),
            self._tab_size[0].to_bytes(1, 'big'),
            self._tab_size[1].to_bytes(1, 'big'),
            self._tab_offset[0].to_bytes(1, 'big'),
            self._tab_offset[1].to_bytes(1, 'big'),
            self._data_size.to_bytes(1, 'big'),
            self._encoding.to_bytes(1, 'big'),
            self._xys[0].to_bytes(2, 'big'),
            self._xys[1].to_bytes(2, 'big'),
            self._xye[0].to_bytes(2, 'big'),
            self._xye[1].to_bytes(2, 'big'),
            self._colour_line.to_bytes(2, 'big'),
            self._colour_text.to_bytes(2, 'big'),
            self._font_id[0].to_bytes(1, 'big'),
            self._font_id[1].to_bytes(1, 'big'),
            self._font_size[0].to_bytes(1, 'big'),
            self._font_size[1].to_bytes(1, 'big'),
            self._hide_col_head.to_bytes(1, 'big'),
            self._hide_row_head.to_bytes(1, 'big')
        ])
    
    @property
    def table_size(self):
        return self._tab_size
    
    @table_size.setter
    def table_size(self, value):
        validate_int_tuple(value, 2, range(1, 256), 'table size')
        self._tab_size = value

    @property
    def table_offset(self):
        return self._tab_offset
    
    @table_offset.setter
    def table_offset(self, value):
        validate_int_tuple(value, 2, range(256), 'table offset')
        self._tab_offset = value
    
    @property
    def data_size(self):
        return self._data_size
    
    @data_size.setter
    def data_size(self, value):
        validate_int(value, range(0x80), 'data size')
        self._data_size = value

    @property
    def encoding(self):
        return self._encoding
    
    @encoding.setter
    def encoding(self, value):
        validate_int(value, range(256), 'encoding')
        self._encoding = value

    @property
    def xy_start(self):
        return self._xys
    
    @xy_start.setter
    def xy_start(self, value):
        validate_coordinates(value)
        self._xys = value
    
    @property
    def xy_end(self):
        return self._xye
    
    @xy_end.setter
    def xy_end(self, value):
        validate_coordinates(value)
        self._xye = value
    
    @property
    def colour_line(self):
        return self._colour_line
    
    @colour_line.setter
    def colour_line(self, value):
        v = validate_colour(value)
        self._colour_line = v
    
    @property
    def colour_text(self):
        return self._colour_text
    
    @colour_text.setter
    def colour_text(self, value):
        v = validate_colour(value)
        self._colour_text = v
    
    @property
    def font_id(self):
        return self._font_id
    
    @font_id.setter
    def font_id(self, value):
        validate_int_tuple(value, 2, range(256), 'font id')
        self._font_id = value
    
    @property
    def font_size(self):
        return self._font_size
    
    @font_size.setter
    def font_size(self, value):
        validate_int_tuple(value, 2, range(256), 'font size')
        self._font_size = value
    
    @property
    def hide_col_header(self):
        return self._hide_col_head
    
    @hide_col_header.setter
    def hide_col_header(self, value):
        validate_bool(value, 'property')
        self._hide_col_head = value
    
    @property
    def hide_row_header(self):
        return self._hide_row_head
    
    @hide_row_header.setter
    def hide_row_header(self, value):
        validate_bool(value, 'property')
        self._hide_row_head = value
