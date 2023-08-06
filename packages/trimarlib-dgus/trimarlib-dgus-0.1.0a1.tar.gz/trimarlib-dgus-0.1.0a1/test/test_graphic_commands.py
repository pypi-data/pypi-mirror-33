import unittest

from dguslib.graphic_commands import DotCommand
from dguslib.graphic_commands import LineCommand
from dguslib.graphic_commands import RectangleCommand
from dguslib.graphic_commands import RectangleAreaFillCommand
from dguslib.graphic_commands import CircleCommand
from dguslib.graphic_commands import PicturePasteCommand
from dguslib.graphic_commands import IconDisplayCommand
from dguslib.graphic_commands import AreaFillCommand
from dguslib.graphic_commands import SpectrumCommand
from dguslib.graphic_commands import SegmentCommand
from dguslib.graphic_commands import ArcDisplayCommand
from dguslib.graphic_commands import CharacterCommand
from dguslib.graphic_commands import RectangleXorCommand
from dguslib.graphic_commands import BicolorGraphCommand
from dguslib.graphic_commands import BitmapCommand
from dguslib.graphic_commands import DisplayZoomCommand

from dguslib.data_packs import BaseDataPack
from dguslib.data_packs import DotDataPack
from dguslib.data_packs import LineDataPack
from dguslib.data_packs import RectangleDataPack
from dguslib.data_packs import CircleDataPack
from dguslib.data_packs import PictureDataPack
from dguslib.data_packs import IconDataPack
from dguslib.data_packs import AreaFillDataPack
from dguslib.data_packs import SpectrumDataPack
from dguslib.data_packs import SegmentDataPack
from dguslib.data_packs import ArcDataPack
from dguslib.data_packs import CharacterDataPack
from dguslib.data_packs import BicolorGraphDataPack
from dguslib.data_packs import BitmapDataPack
from dguslib.data_packs import DisplayZoomDataPack


class TestGraphicCommands(unittest.TestCase):

    def test_DotCommand(self):
        self._test_command(DotCommand,
                           DotDataPack,
                           ((0, 0), 0))

    def test_LineCommand(self):

        cmd = LineCommand()
        with self.assertRaises(IndexError):
            cmd[0]
        len_empty = len(cmd)
        self.assertEqual(len(bytes(cmd)), len(cmd))

        dp = LineDataPack(0, [])
        cmd += dp
        with self.assertRaises(RuntimeError):
            bytes(cmd)
        cmd[0] += (0, 0)
        cmd[0] += (1, 1)
        self.assertEqual(len(bytes(cmd)), len(cmd))
        self.assertEqual(len(cmd), len_empty + len(dp))
        self.assertIs(type(cmd[0]), LineDataPack)

        for d in [BaseDataPack(),
                  DotDataPack((0, 0), 0),
                  LineDataPack(0, []),
                  RectangleDataPack((0, 0), (0, 0), 0),
                  CircleDataPack((0, 0), 0, 0),
                  PictureDataPack(0, (0, 0), (0, 0), (0, 0)),
                  IconDataPack((0, 0), 0),
                  AreaFillDataPack((0, 0), 0),
                  SpectrumDataPack(0, 0, 0, 0),
                  SegmentDataPack(0, (0, 0), (0, 0)),
                  ArcDataPack(0, (0, 0), 0, 0, 0),
                  CharacterDataPack(0, (0, 0), 0, 0, (0, 0), 0),
                  BicolorGraphDataPack((0, 0), (0, 0), 0, 0),
                  BitmapDataPack((0, 0), (0, 0)),
                  DisplayZoomDataPack((0, 0), (0, 0), (0, 0))]:
            with self.subTest(type=type(d)):
                with self.assertRaises((TypeError, RuntimeError)):
                    cmd += d

        cmd = LineCommand(dp)
        with self.assertRaises(RuntimeError):
            cmd = LineCommand([dp, dp])

    def test_RectangleCommand(self):
        self._test_command(RectangleCommand,
                           RectangleDataPack,
                           ((0, 0), (0, 0), 0))

    def test_RectangleAreaFillCommand(self):
        self._test_command(RectangleAreaFillCommand,
                           RectangleDataPack,
                           ((0, 0), (0, 0), 0))

    def test_CircleCommand(self):
        self._test_command(CircleCommand,
                           CircleDataPack,
                           ((0, 0), 0, 0))

    def test_PicturePasteCommand(self):
        self._test_command(PicturePasteCommand,
                           PictureDataPack,
                           (0, (0, 0), (0, 0), (0, 0)))

    def test_IconDisplayCommand(self):

        cmd = IconDisplayCommand(0)
        with self.assertRaises(IndexError):
            cmd[0]
        len_empty = len(cmd)
        self.assertEqual(len(bytes(cmd)), len(cmd))

        dp = IconDataPack((0, 0), 0)
        cmd += dp
        self.assertEqual(len(bytes(cmd)), len(cmd))
        self.assertEqual(len(cmd), len_empty + len(dp))
        self.assertIs(type(cmd[0]), IconDataPack)

        for d in [BaseDataPack(),
                  DotDataPack((0, 0), 0),
                  LineDataPack(0, []),
                  RectangleDataPack((0, 0), (0, 0), 0),
                  CircleDataPack((0, 0), 0, 0),
                  PictureDataPack(0, (0, 0), (0, 0), (0, 0)),
                  IconDataPack((0, 0), 0),
                  AreaFillDataPack((0, 0), 0),
                  SpectrumDataPack(0, 0, 0, 0),
                  SegmentDataPack(0, (0, 0), (0, 0)),
                  ArcDataPack(0, (0, 0), 0, 0, 0),
                  CharacterDataPack(0, (0, 0), 0, 0, (0, 0), 0),
                  BicolorGraphDataPack((0, 0), (0, 0), 0, 0),
                  BitmapDataPack((0, 0), (0, 0)),
                  DisplayZoomDataPack((0, 0), (0, 0), (0, 0))]:
            if type(d) is IconDataPack:
                continue
            with self.subTest(type=type(d)):
                with self.assertRaises(TypeError):
                    cmd += d

        cmd = IconDisplayCommand(0, dp)
        cmd = IconDisplayCommand(0, [dp, dp])

    def test_AreaFillCommand(self):
        self._test_command(AreaFillCommand,
                           AreaFillDataPack,
                           ((0, 0), 0))

    def test_SpectrumCommand(self):
        self._test_command(SpectrumCommand,
                           SpectrumDataPack,
                           (0, 0, 0, 0))

    def test_SegmentCommand(self):
        self._test_command(SegmentCommand,
                           SegmentDataPack,
                           (0, (0, 0), (0, 0)))

    def test_ArcDisplayCommand(self):
        self._test_command(ArcDisplayCommand,
                           ArcDataPack,
                           (0, (0, 0), 0, 0, 0))

    def test_CharacterCommand(self):
        self._test_command(CharacterCommand,
                           CharacterDataPack,
                           (0, (0, 0), 0, 0, (0, 0), 0))

    def test_RectangleXorCommand(self):
        self._test_command(RectangleXorCommand,
                           RectangleDataPack,
                           ((0, 0), (0, 0), 0))

    def test_BicolorGraphCommand(self):
        self._test_command(BicolorGraphCommand,
                           BicolorGraphDataPack,
                           ((0, 0), (0, 0), 0, 0))

    def test_BitmapCommand(self):
        self._test_command(BitmapCommand,
                           BitmapDataPack,
                           ((0, 0), (0, 0)))

    def test_DisplayZoomCommand(self):
        self._test_command(DisplayZoomCommand,
                           DisplayZoomDataPack,
                           ((0, 0), (0, 0), (0, 0)))

    def _test_command(self, cmd_cls, dp_cls, dp_args):

        cmd = cmd_cls()
        with self.assertRaises(IndexError):
            cmd[0]
        len_empty = len(cmd)
        self.assertEqual(len(bytes(cmd)), len(cmd))

        dp = dp_cls(*dp_args)
        cmd += dp
        self.assertEqual(len(bytes(cmd)), len(cmd))
        self.assertEqual(len(cmd), len_empty + len(dp))
        self.assertIs(type(cmd[0]), dp_cls)

        for d in [BaseDataPack(),
                  DotDataPack((0, 0), 0),
                  LineDataPack(0, []),
                  RectangleDataPack((0, 0), (0, 0), 0),
                  CircleDataPack((0, 0), 0, 0),
                  PictureDataPack(0, (0, 0), (0, 0), (0, 0)),
                  IconDataPack((0, 0), 0),
                  AreaFillDataPack((0, 0), 0),
                  SpectrumDataPack(0, 0, 0, 0),
                  SegmentDataPack(0, (0, 0), (0, 0)),
                  ArcDataPack(0, (0, 0), 0, 0, 0),
                  CharacterDataPack(0, (0, 0), 0, 0, (0, 0), 0),
                  BicolorGraphDataPack((0, 0), (0, 0), 0, 0),
                  BitmapDataPack((0, 0), (0, 0)),
                  DisplayZoomDataPack((0, 0), (0, 0), (0, 0))]:
            if type(d) is dp_cls:
                continue
            with self.subTest(type=type(d)):
                with self.assertRaises(TypeError):
                    cmd += d

        cmd = cmd_cls(dp)
        cmd = cmd_cls([dp, dp])



