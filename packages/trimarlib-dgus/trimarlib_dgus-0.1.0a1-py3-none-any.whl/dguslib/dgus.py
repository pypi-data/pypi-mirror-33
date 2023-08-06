import enum
import time
import threading
import serial
import crcmod
from functools import wraps
from .graphic_commands import GraphicCommand


class TouchStatus(enum.IntEnum):
    touch_none = 0
    touch_begin = 1
    touch_end = 2
    touch_continue = 3


def _locked(fn):
    @wraps(fn)
    def _fn(self, *args, **kwargs):
        with self._port_rlock:
            ret = fn(self, *args, **kwargs)
        return ret
    return _fn


class LCD(object):
    """Representation of the DWIN DGUS display."""

    REG_VERSION = 0x00
    REG_BACKLIGHT = 0x01
    REG_BUZZER = 0x02
    REG_PICID = 0x03
    REG_TPFLAG = 0x05
    REG_TPSTATUS = 0x06
    REG_TPPOSITION = 0x07
    REG_TPCENABLE = 0x0B
    REG_RUNTIME = 0x0C
    REG_SDCONFIG = 0x10
    REG_RTCADJ = 0x1F
    REG_RTC = 0x20
    REG_TIM0 = 0x4A
    REG_TIM1 = 0x4C
    REG_TIM2 = 0x4D
    REG_TIM3 = 0x4E
    REG_KEYCODE = 0x4F
    REG_TRENDLINE_CLEAR = 0xEB
    REG_RESET = 0xEE

    def __init__(self, port, *, baudrate=115200, timeout=2, crc=True, header=b'\xAA\xBB'):
        """Initializes object instance.

        Parameters
        ----------
        port : str or Serial
            path to the serial port to use or an instance of Serial object
        baudrate : int
        timeout : float
        crc : bool
            indicates whether checksum is to be used when communicating
            with the display
        header : iterable
            list of integers, bytes or bytearray defining frame header
        """
        if type(port) is serial.Serial:
            self._port = port
        elif type(port) is str:
            self._port = serial.Serial(port)
        else:
            raise TypeError()
        if timeout is not None:
            self._port.apply_settings({'timeout': timeout})
        if baudrate is not None:
            self._port.apply_settings({'baudrate': baudrate})
        self._port_rlock = threading.RLock()

        if crc:
            self._crc_fun = crcmod.mkCrcFun(0x18005)
        else:
            self._crc_fun = None

        self._header = bytes(header)
        if len(self._header) != 2:
            raise ValueError('header is required to be 2 bytes in length')

        return

    def __del__(self):
        try:
            self._port.close()
            del self._port
        except AttributeError:
            pass

    @_locked
    def _write_frame(self, data):
        if self._crc_fun is None:
            crcbytes = b''
            datalen = (len(data)).to_bytes(1, 'little')
        else:
            crcbytes = self._crc_fun(data).to_bytes(2, 'little')
            datalen = (len(data) + 2).to_bytes(1, 'little')
        self._port.write(self._header)
        self._port.write(datalen)
        self._port.write(data)
        self._port.write(crcbytes)
        return

    @_locked
    def _read_frame(self):
        head = self._port.read(2)
        if len(head) != 2:
            raise TimeoutError('Missing header bytes')
        while head != self._header:
            b = self._port.read(1)
            if len(b) != 1:
                raise TimeoutError('Missing header bytes')
            head = head[1] + b
        datalen = self._port.read(1)
        if len(datalen) != 1:
            raise TimeoutError('Missing data length byte')
        datalen = int.from_bytes(datalen, 'little')
        data = self._port.read(datalen)
        if len(data) != datalen:
            raise TimeoutError('Missing data bytes, received {} out of {}'.format(len(data), datalen))
        if self._crc_fun is not None:
            if self._crc_fun(data) != 0:
                raise ValueError('CRC mismatch')
            data = data[0:-2]
        return data

    @_locked
    def write_regs(self, addr, data):
        """Writes data to register at provided address."""
        txdata = b'\x80' + addr.to_bytes(1, 'big') + data
        self._write_frame(txdata)
        return

    @_locked
    def read_regs(self, addr, num):
        """Reads contents of registers at provided address."""
        txdata = b'\x81' + addr.to_bytes(1, 'big') + num.to_bytes(1, 'big')
        self._write_frame(txdata)
        rxdata = self._read_frame()
        if not rxdata.startswith(txdata):
            raise ValueError('Unexpected data')
        return rxdata[len(txdata)::]

    @_locked
    def write_ram(self, addr, data):
        """Writes data to RAM at provided address."""
        offs = 0
        rem = len(data)
        if issubclass(type(data), GraphicCommand):
            data = bytes(data)
        while rem > 0:
            dlen = 250 if rem > 250 else rem
            txdata = b''.join([b'\x82', addr.to_bytes(2, 'big'), data[offs:offs+dlen]])
            self._write_frame(txdata)
            addr += dlen >> 1
            offs += dlen
            rem -= dlen
        return

    @_locked
    def read_ram(self, addr, num):
        """Reads contents of RAM memory at provided address."""
        txdata = b'\x83' + addr.to_bytes(2, 'big') + num.to_bytes(1, 'big')
        self._write_frame(txdata)
        rxdata = self._read_frame()
        if not rxdata.startswith(txdata):
            raise ValueError('Unexpected data')
        return rxdata[len(txdata)::]

    @_locked
    def write_curve(self, channels, *data):
        """Writes data to curve buffer.

        Parameters
        ----------
        channels : 1-byte integer
            bit mask of channels whose data is being sent
        data : lists of integers in range(0x10000) (for single channel) or list of lists
            curve data; if writing to single channel it has to be a list of unsigned short integers; if writing to
            more than one channel at once it has to be a list or a tuple of lists (of equal lengths) of unsigned short
            integers, ordered by channel index, lower indices first
        """
        if channels == 0:
            return
        channels_count = 0
        for offs in range(8):
            if (channels & (1 << offs)) != 0:
                channels_count += 1
        data_bytes = bytearray()
        for d in zip(*data[:channels_count]):
            for dd in d:
                data_bytes.extend(dd.to_bytes(2, 'big'))

        chunk_size = channels_count * 2
        chunk_rem = int(len(data_bytes) / chunk_size)
        chunk_max = int(250 / chunk_size)
        chunk_offs = 0
        header = b''.join([b'\x84', channels.to_bytes(1, 'big')])

        while chunk_rem > 0:
            chunk_cnt = chunk_max if chunk_rem > chunk_max else chunk_rem
            d_offs = chunk_size * chunk_offs
            d_len = chunk_size * chunk_cnt
            txdata = b''.join([header, data_bytes[d_offs:d_offs+d_len]])
            self._write_frame(txdata)
            chunk_offs += chunk_cnt
            chunk_rem -= chunk_cnt

    def get_version(self):
        """Returns tuple (major, minor) representing display firmware version."""
        b = self.read_regs(self.REG_VERSION, 1)
        return b[0] >> 4, b[0] & 0x0F

    @property
    def version(self):
        """Convenience wrapper around get_version method."""
        return self.get_version()

    def reset(self):
        """Resets display."""
        self.write_regs(self.REG_RESET, b'\x5A\xA5')
        return

    def get_backlight(self):
        """Reads backlight intensity and returns floating point value in percents."""
        b = self.read_regs(self.REG_BACKLIGHT, 1)
        val = int.from_bytes(b, 'big')
        return 100 * val / 0x40

    def set_backlight(self, val):
        """Sets backlight intensity. Value passed as parameter is interpreted as percents."""
        if val < 0 or val > 100:
            raise ValueError('Backlight value out of range <0,100>')
        val = int((val * 0x40) / 100)
        self.write_regs(self.REG_BACKLIGHT, val.to_bytes(1, 'big'))
        return

    @property
    def backlight(self):
        """Property wrapper around get_* and set_backlight methods."""
        return self.get_backlight()

    @backlight.setter
    def backlight(self, v):
        self.set_backlight(v)

    def enable_backlight(self):
        """Convenience wrapper that sets backlight to max value (100%)."""
        self.backlight = 100

    def disable_backlight(self):
        """Convenience wrapper that sets backlight to min value (10%)."""
        self.backlight = 10

    def buzzer(self, val):
        """Enables buzzer operation, passed value is interpreted as
        floating point time expressed in seconds."""
        v = int(val * 100)
        self.write_regs(self.REG_BUZZER, v.to_bytes(1, 'big'))
        return

    def get_picture_id(self):
        """Reads ID of current background picture."""
        b = self.read_regs(self.REG_PICID, 2)
        return int.from_bytes(b, 'big')

    def set_picture_id(self, picid):
        """Sets background picture ID."""
        self.write_regs(self.REG_PICID, picid.to_bytes(2, 'big'))

    @property
    def picture_id(self):
        """Convenience property wrapper around get_* and set_picture_id
        methods."""
        return self.get_picture_id()

    @picture_id.setter
    def picture_id(self, value):
        self.set_picture_id(value)

    def get_touch_flag(self):
        """Returns boolean flag indicating whether update of touch
        coordinates occurred."""
        b = self.read_regs(self.REG_TPFLAG, 1)
        return True if b[0] == 0x5A else False

    def clear_touch_flag(self):
        """Clears touch flag."""
        self.write_regs(self.REG_TPFLAG, b'\x00')

    @property
    @_locked
    def touch_flag(self):
        """Property wrapper around get_* and clear_touch_flag methods.

        NOTE: Reading flag using this property automatically clears it.
        """
        v = self.get_touch_flag()
        self.clear_touch_flag()
        return v

    def get_touch_status(self):
        """Reads touch status, returns TouchStatus object."""
        b = self.read_regs(self.REG_TPSTATUS, 1)
        try:
            return TouchStatus(b[0])
        except ValueError:
            pass
        return TouchStatus.touch_none

    @property
    def touch_status(self):
        """Convenience wrapper around get_touch_status method."""
        return self.get_touch_status()

    def get_touch_position(self):
        """Reads touch coordinates and returns a tuple (X, Y)."""
        b = self.read_regs(self.REG_TPPOSITION, 4)
        x = int.from_bytes(b[0:2], 'big')
        y = int.from_bytes(b[2:4], 'big')
        return x, y

    @property
    def touch_position(self):
        """Convenience property wrapper around get_touch_position method."""
        return self.get_touch_position()

    def get_touch_enabled(self):
        """Returns boolean value indicating whether touch panel is enabled."""
        b = self.read_regs(self.REG_TPCENABLE, 1)
        return True if b[0] != 0 else False

    def set_touch_enabled(self, enabled=True):
        """Enables or disables touch panel."""
        if bool(enabled):
            arg = b'\xFF'
        else:
            arg = b'\x00'
        self.write_regs(self.REG_TPCENABLE, arg)

    @property
    def touch_enabled(self):
        """Convenience wrapper around get_* and set_touch_enabled methods."""
        return self.get_touch_enabled()

    @touch_enabled.setter
    def touch_enabled(self, v):
        self.set_touch_enabled(v)

    def get_runtime(self):
        """Reads runtime of the display, returns it as a tuple (hours, minutes, seconds)."""
        b = self.read_regs(self.REG_RUNTIME, 4)
        hrs = ((b[0] >> 4) * 1000) + ((b[0] & 0x0F) * 100) + ((b[1] >> 4) * 10) + (b[1] & 0x0F)
        mns = ((b[2] >> 4) * 10) + (b[2] & 0x0F)
        ss = ((b[3] >> 4) * 10) + (b[3] & 0x0F)
        return hrs, mns, ss

    @property
    def runtime(self):
        """Convenience wrapper around get_runtime method."""
        return self.get_runtime()

    def config_regs(self):
        """Reads configuration registers, returns them as a bytes object."""
        return self.read_regs(self.REG_SDCONFIG, 11)

    def get_rtc(self):
        """Reads RTC value from the display and returns it as a time.struct_time."""
        b = self.read_regs(self.REG_RTC, 16)
        tm = time.struct_time((
            2000 + ((b[0] >> 4) * 10) + (b[0] & 0x0F),
            ((b[1] >> 4) * 10) + (b[1] & 0x0F),
            ((b[2] >> 4) * 10) + (b[2] & 0x0F),
            ((b[4] >> 4) * 10) + (b[4] & 0x0F),
            ((b[5] >> 4) * 10) + (b[5] & 0x0F),
            ((b[6] >> 4) * 10) + (b[6] & 0x0F),
            ((b[3] >> 4) * 10) + (b[3] & 0x0F) - 1,
            0, 0
        ))
        return tm

    @property
    def rtc(self):
        """Convenience wrapper around get_rtc method."""
        return self.get_rtc()

    def set_rtc(self, tm=None):
        """Sets RTC value stored in the display. If argument passed is
        None, adjusts RTC value to local time of the system. Otherwise
        the function accepts a floating point value as UNIX timestamp
        (as obtained from time.time function) or a time.struct_time
        object."""
        if tm is None:
            tm = time.localtime()
        elif type(tm) is not time.struct_time:
            tm = time.localtime(tm)
        data = b''.join([
            b'\x5A',
            ((int((tm.tm_year / 10) % 10) << 4) | int(tm.tm_year % 10)).to_bytes(1, 'big'),
            ((int((tm.tm_mon / 10) % 10) << 4) | int(tm.tm_mon % 10)).to_bytes(1, 'big'),
            ((int((tm.tm_mday / 10) % 10) << 4) | int(tm.tm_mday % 10)).to_bytes(1, 'big'),
            ((int(((tm.tm_wday + 1) / 10) % 10) << 4) | int((tm.tm_wday + 1) % 10)).to_bytes(1, 'big'),
            ((int((tm.tm_hour / 10) % 10) << 4) | int(tm.tm_hour % 10)).to_bytes(1, 'big'),
            ((int((tm.tm_min / 10) % 10) << 4) | int(tm.tm_min % 10)).to_bytes(1, 'big'),
            ((int((tm.tm_sec / 10) % 10) << 4) | int(tm.tm_sec % 10)).to_bytes(1, 'big')
        ])
        self.write_regs(self.REG_RTCADJ, data)

    def access_lib(self, op, libid, liboffs, vp, oplen):
        """Performs a font flash memory access as defined in DWIN DGUS
        documentation.

        Parameters
        ----------
        op : int
            type of operation, 0x50 transfers data from RAM to font
            flash memory, 0xA0 transfers data from font flash memory to
            RAM.
        libid : int
            indicates font flash memory sector, must be in range
            <0x40, 0x80).
        liboffs : int
            offset in font flash memory sector.
        vp : int
            address in RAM memory, must be in range <0x0000, 0x7000).
        oplen : int
            length of data to transfer.
        """
        if op != 0x50 and op != 0xA0:
            raise ValueError('invalid operation value')
        if libid < 0x40 or libid > 0x7F:
            raise ValueError('invalid library id')
        if liboffs >= 0x20000 or (liboffs + oplen) > 0x20000:
            raise ValueError('invalid library offset')
        if vp >= 0x7000 or (vp + oplen) > 0x7000:
            raise ValueError('invalid RAM address')
        bb = b'\x5A'
        bb += op.to_bytes(1, 'big')
        bb += libid.to_bytes(1, 'big')
        bb += liboffs.to_bytes(3, 'big')
        bb += vp.to_bytes(2, 'big')
        bb += oplen.to_bytes(2, 'big')
        self.write_regs(0x40, bb)

        bb = self.read_regs(0x40, 1)
        while bb[0] != 0:
            bb = self.read_regs(0x40, 1)

    def load_lib(self, libid, liboffs, vp, oplen):
        """Convenience wrapper around access_lib method with op argument
        set to 0xA0 (transfer from library to RAM).
        """
        self.access_lib(0xA0, libid, liboffs, vp, oplen)

    def store_lib(self, libid, liboffs, vp, oplen):
        """Convenience wrapper around access_lib method with op argument
        set to 0x50 (transfer from library to RAM).
        """
        self.access_lib(0x50, libid, liboffs, vp, oplen)

    def get_timer(self, timid):
        """Reads value of the software timer implemented in the display,
        returns remaining time in milliseconds."""
        if timid == 0:
            reg = 0x4A
            regcnt = 2
        elif timid < 4:
            reg = 0x4C + (timid - 1)
            regcnt = 1
        else:
            raise ValueError()
        bb = self.read_regs(reg, regcnt)
        return int.from_bytes(bb, 'big') * 4

    def set_timer(self, timid, val):
        """Writes value to the software timer implemented in the display,
        passed value is interpreted as milliseconds."""
        if timid == 0:
            reg = 0x4A
            regcnt = 2
        elif timid < 4:
            reg = 0x4C + (timid-1)
            regcnt = 1
        else:
            raise ValueError()
        v = int(val / 4)
        self.write_regs(reg, v.to_bytes(regcnt, 'big'))

    @property
    def timer0(self):
        """Property wrapper around get_* and set_timer methods with timer
        ID set to 0."""
        return self.get_timer(0)

    @timer0.setter
    def timer0(self, val):
        self.set_timer(0, val)

    @property
    def timer1(self):
        """Property wrapper around get_* and set_timer methods with timer
        ID set to 1."""
        return self.get_timer(1)

    @timer1.setter
    def timer1(self, val):
        self.set_timer(1, val)

    @property
    def timer2(self):
        """Property wrapper around get_* and set_timer methods with timer
        ID set to 2."""
        return self.get_timer(2)

    @timer2.setter
    def timer2(self, val):
        self.set_timer(2, val)

    @property
    def timer3(self):
        """Property wrapper around get_* and set_timer methods with timer
        ID set to 3."""
        return self.get_timer(3)

    @timer3.setter
    def timer3(self, val):
        self.set_timer(3, val)
