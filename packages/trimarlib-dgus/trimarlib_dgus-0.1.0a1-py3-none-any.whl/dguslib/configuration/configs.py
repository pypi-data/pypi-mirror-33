from ..helpers import validate_ushort
from . import descriptors


class VariableConfiguration(object):
    """Abstraction class for variable configuration."""

    __slots__ = '_code', '_length', '_sp', '_desc', '_desc_type'

    def __init__(self, code, length, desc_type, desc=None, sp=0xFFFF):
        self._sp = None
        self.sp = sp
        if type(code) is not int:
            raise TypeError('code')
        if code not in range(256):
            raise ValueError('code')
        self._code = code
        if type(length) is not int:
            raise TypeError('length')
        if length not in range(0x10000):
            raise ValueError('length')
        self._length = length
        if not issubclass(desc_type, descriptors.VariableDescriptor):
            raise TypeError('descriptor type')
        self._desc_type = desc_type
        if desc is not None and type(desc) is not desc_type:
            raise TypeError('descriptor')
        self._desc = desc

    @property
    def sp(self):
        return self._sp

    @sp.setter
    def sp(self, value):
        validate_ushort(value, 'stack pointer')
        self._sp = value

    @property
    def code(self):
        return self._code

    @property
    def length(self):
        return self._length

    @property
    def descriptor(self):
        return self._desc

    @descriptor.setter
    def descriptor(self, value):
        if value is None or type(value) is self._desc_type:
            self._desc = value
        else:
            raise TypeError('invalid descriptor type')

    def __bytes__(self):
        bb = b''.join([
            b'\x5A',
            self._code.to_bytes(1, 'big'),
            self._sp.to_bytes(2, 'big'),
            self._length.to_bytes(2, 'big')])
        if self._desc is not None:
            bb = b''.join([bb, bytes(self._desc)])
        bb = b''.join([bb, bytes(32 - len(bb))])
        return bb


class VariableIcon(VariableConfiguration):
    _CODE = 0x00
    _LENGTH = 0x0008

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.VariableIconDescriptor, desc, sp)


class AnimationIcon(VariableConfiguration):
    _CODE = 0x01
    _LENGTH = 0x000A

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.AnimationIconDescriptor, desc, sp)


class Slider(VariableConfiguration):
    _CODE = 0x02
    _LENGTH = 0x0009

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.SliderDescriptor, desc, sp)


class WordArt(VariableConfiguration):
    _CODE = 0x03
    _LENGTH = 0x0007

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.WordArtDescriptor, desc, sp)


class ImageAnimation(VariableConfiguration):
    _CODE = 0x04
    _LENGTH = 0x0004

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.ImageAnimationDescriptor, desc, sp)


class IconRotation(VariableConfiguration):
    _CODE = 0x05
    _LENGTH = 0x000C

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.IconRotationDescriptor, desc, sp)


class BitVariable(VariableConfiguration):
    _CODE = 0x06
    _LENGTH = 0x000C

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.BitVariableDescriptor, desc, sp)


class DataVariable(VariableConfiguration):
    _CODE = 0x10
    _LENGTH = 0x000D

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.DataVariableDescriptor, desc, sp)


class Text(VariableConfiguration):
    _CODE = 0x11
    _LENGTH = 0x000D

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.TextDescriptor, desc, sp)


class DigitalRTC(VariableConfiguration):
    _CODE = 0x12
    _LENGTH = 0x000D

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.DigitalRTCDescriptor, desc, sp)


class AnalogRTC(VariableConfiguration):
    _CODE = 0x12
    _LENGTH = 0x000D

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.AnalogRTCDescriptor, desc, sp)


class HexVariable(VariableConfiguration):
    _CODE = 0x13
    _LENGTH = 0x000D

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.HexVariableDescriptor, desc, sp)


class DynamicTrendCurve(VariableConfiguration):
    _CODE = 0x20
    _LENGTH = 0x000A

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.DynamicTrendCurveDescriptor, desc, sp)


class BasicGraphics(VariableConfiguration):
    _CODE = 0x21
    _LENGTH = 0x0008

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.BasicGraphicsDescriptor, desc, sp)


class Table(VariableConfiguration):
    _CODE = 0x22
    _LENGTH = 0x000C

    def __init__(self, desc=None, sp=0xFFFF):
        super().__init__(self._CODE, self._LENGTH, descriptors.TableDescriptor, desc, sp)
