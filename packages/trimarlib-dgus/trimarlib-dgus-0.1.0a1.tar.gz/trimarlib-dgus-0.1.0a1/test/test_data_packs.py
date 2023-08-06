import unittest
from dguslib.data_packs import DotDataPack
from dguslib.data_packs import LineDataPack
from dguslib.data_packs import RectangleDataPack
from dguslib.data_packs import CircleDataPack
from dguslib.data_packs import IconDataPack
from dguslib.data_packs import PictureDataPack
from dguslib.data_packs import AreaFillDataPack
from dguslib.data_packs import SpectrumDataPack
from dguslib.data_packs import SegmentDataPack
from dguslib.data_packs import ArcDataPack
from dguslib.data_packs import CharacterDataPack
from dguslib.data_packs import BicolorGraphDataPack
from dguslib.data_packs import BitmapDataPack
from dguslib.data_packs import DisplayZoomDataPack


class TestDataPacks(unittest.TestCase):

    def test_DotDataPack_init(self):

        for xy, colour, exc in [(None, None, TypeError),
                                ((), 0, TypeError),
                                ((0,), 0, TypeError),
                                ((0, 'a'), 0, TypeError),
                                ((3.14, 4.75), 0, TypeError),
                                ((0, 0), 3.14, TypeError),
                                ((-1, 0), 0, ValueError),
                                ((0, -1), 0, ValueError),
                                ((0, 0), 'unknown', ValueError)]:
            with self.subTest(xy=xy, colour=colour):
                with self.assertRaises(exc):
                    dp = DotDataPack(xy, colour)

        dp = DotDataPack((0, 0), 0)
        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(len(dp.xy), 2)
        for i in range(2):
            self.assertIs(type(dp.xy[i]), int)
            self.assertEqual(dp.xy[i], 0)
        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        self.assertEqual(len(bytes(dp)), len(dp))
        del dp

    def test_DotDataPack_xy(self):

        for xy in [(0, 0x10000), (0x10000, 0)]:
            with self.subTest(xy=xy):
                with self.assertRaises(ValueError):
                    dp = DotDataPack(xy, 0)

        dp = DotDataPack((0, 0), 0)
        for xy, exc in [(None, TypeError),
                        ([], TypeError),
                        ({}, TypeError),
                        (3.14, TypeError),
                        ((0,), TypeError),
                        ((0, .1), TypeError),
                        ((0, -1), ValueError),
                        ((0, 0x10000), ValueError)]:
            with self.subTest(xy=xy):
                with self.assertRaises(exc):
                    dp.xy = xy

    def test_DotDataPack_colour(self):

        for colour in [-1, 0x10000]:
            with self.subTest(colour=colour):
                with self.assertRaises(ValueError):
                    dp = DotDataPack((0, 0), colour)

        dp = DotDataPack((0, 0), 0)
        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (3.14, TypeError),
                            (-1, ValueError),
                            (0x10000, ValueError),
                            ('', ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    dp.colour = colour

    def test_LineDataPack_init(self):

        for colour, vertices, exc in [(None, (0, 0) , TypeError),
                                      (3.14, (0, 0), TypeError),
                                      ('', (0, 0), ValueError),
                                      (0, None, TypeError),
                                      (0, (), TypeError),
                                      (0, ('',), TypeError),
                                      (0, ('', 0), TypeError),
                                      (0, (0, ''), TypeError),
                                      (0, (.1,), TypeError),
                                      (0, (.1, 0), TypeError),
                                      (0, (0, .1), TypeError),
                                      (0, (0, -1), ValueError),
                                      (0, (-1, 0), ValueError),
                                      (0, [(0, 0), (0,)], TypeError),
                                      (0, [(0, 0), (0, '')], TypeError),
                                      (0, [(0, 0), (0, -1)], ValueError),
                                      (0, [(0, 0), (-1, 0)], ValueError)]:
            with self.subTest(colour=colour, vertices=vertices):
                with self.assertRaises(exc):
                    dp = LineDataPack(colour, vertices)

    def test_LineDataPack_colour(self):

        for colour in [-1, 0x10000]:
            with self.subTest(colour=colour):
                with self.assertRaises(ValueError):
                    dp = LineDataPack(colour, [(0, 0), (0, 0)])

        dp = LineDataPack(0, [(0, 0), (0, 0)])
        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)
        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (3.14, TypeError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    dp.colour = colour

    def test_LineDataPack_vertices(self):

        dp = LineDataPack(0, [])
        with self.assertRaises(IndexError):
            dp[0]
        with self.assertRaises(RuntimeError):
            bytes(dp)

        for other, exc in [((), TypeError),
                           ((0,), TypeError),
                           ((0, 3.14), TypeError),
                           ((0, ''), TypeError),
                           ((.1, 0), TypeError),
                           (('', 0), TypeError),
                           ((-1, 0), ValueError),
                           ((0, -1), ValueError)]:
            with self.subTest(other=other):
                with self.assertRaises(exc):
                    dp += other

        dp += (0, 0)
        with self.assertRaises(RuntimeError):
            bytes(dp)
        dp += [(0, 64), (64, 0)]
        self.assertEqual(len(bytes(dp)), len(dp))

        for idx, xy in enumerate([(0, 0), (0, 64), (64, 0)]):
            self.assertEqual(dp[idx], xy)

        with self.assertRaises(ValueError):
            dp += (0, 0x10000)
        with self.assertRaises(ValueError):
            dp[-1] = (0x10000, 0)
        dp[-1] = (0, 0)

        dp = LineDataPack(0, [(0, 0), (1, 1), (2, 2)])
        self.assertEqual(dp[:2], [(0, 0), (1, 1)])
        self.assertEqual(dp[1:], [(1, 1), (2, 2)])
        with self.assertRaises(TypeError):
            dp[:2] = (13, 13)
        with self.assertRaises(TypeError):
            dp[:2] = [(0, 0), (0, 3.14)]
        with self.assertRaises(ValueError):
            dp[:2] = [(0, 0), (-1, 0)]

    def test_RectangleDataPack_init(self):

        for colour, xys, xye, exc in [(.1, None, None, TypeError),
                                      ('', None, None, ValueError),
                                      (0, (), None, TypeError),
                                      (0, (1,), None, TypeError),
                                      (0, (.1,), None, TypeError),
                                      (0, ('',), None, TypeError),
                                      (0, (0, .1), None, TypeError),
                                      (0, (0, ''), None, TypeError),
                                      (0, (0, -1), None, ValueError),
                                      (0, (-1, 0), None, ValueError),
                                      (0, None, (), TypeError),
                                      (0, None, (1,), TypeError),
                                      (0, None, (.1,), TypeError),
                                      (0, None, ('',), TypeError),
                                      (0, None, (0, .1), TypeError),
                                      (0, None, (0, ''), TypeError),
                                      (0, None, (0, -1), ValueError),
                                      (0, None, (-1, 0), ValueError),
                                      (0, (0, 0, 0), None, TypeError),
                                      (0, None, (0, 0, 0), TypeError)]:
            with self.subTest(colour=colour, xys=xys, xye=xye):
                with self.assertRaises(exc):
                    dp = RectangleDataPack(xys, xye, colour)

        for colour, xys, xye in [(0, None, None),
                                 (0, (0, 0), None),
                                 (0, None, (0, 0)),
                                 (0, (0, 0), (0, 0))]:
            dp = RectangleDataPack(xys, xye, colour)
            with self.subTest(colour=colour, xys=xys, xye=xye):
                self.assertIs(type(dp.colour), int)
                self.assertEqual(dp.colour, colour)
                if xys is None:
                    self.assertIs(dp.xy_start, None)
                else:
                    self.assertIs(type(dp.xy_start), tuple)
                    self.assertEqual(len(dp.xy_start), 2)
                    self.assertEqual(dp.xy_start, xys)
                if xye is None:
                    self.assertIs(dp.xy_end, None)
                else:
                    self.assertIs(type(dp.xy_end), tuple)
                    self.assertEqual(len(dp.xy_end), 2)
                    self.assertEqual(dp.xy_end, xye)

        dp = RectangleDataPack((0, 0), (800, 480), 'black')
        self.assertEqual(len(bytes(dp)), len(dp))

    def test_RectangleDataPack_colour(self):

        dp = RectangleDataPack((0, 0), (0, 0), 0)
        for colour in [-1, 0x10000]:
            with self.subTest(colour=colour):
                with self.assertRaises(ValueError):
                    dp.colour = colour

        for colour in [3.14, [], {}, object()]:
            with self.subTest(colour=colour):
                with self.assertRaises(TypeError):
                    dp.colour = colour
        with self.assertRaises(ValueError):
            dp.colour = ''

    def test_RectangleDataPack_coordinates(self):

        dp = RectangleDataPack((0, 0), (0, 0), 0)
        for xy, exc in [(None, TypeError),
                        ({}, TypeError),
                        ([], TypeError),
                        ([0, 0], TypeError),
                        ((), TypeError),
                        ((0,), TypeError),
                        ((0, .1), TypeError),
                        ((0, -1), ValueError),
                        ((0, 0x10000), ValueError)]:
            with self.subTest(xy=xy):
                with self.assertRaises(exc):
                    dp.xy_start = xy
                with self.assertRaises(exc):
                    dp.xy_end = xy

    def test_CircleDataPack(self):

        for args, exc in [((None, 0, 0), TypeError),
                          ((0, 0, 0), TypeError),
                          ((.1, 0, 0), TypeError),
                          (([], 0, 0), TypeError),
                          (({}, 0, 0), TypeError),
                          (((0,), 0, 0), TypeError),
                          (((0, 0, 0), 0, 0), TypeError),
                          (((0, .1), 0, 0), TypeError),
                          (((0, ''), 0, 0), TypeError),
                          (((0, -1), 0, 0), ValueError),
                          (((-1, 0), 0, 0), ValueError),
                          (((0, 0x10000), 0, 0), ValueError),
                          (((0x10000, 0), 0, 0), ValueError),
                          (((0, 0), None, 0), TypeError),
                          (((0, 0), [], 0), TypeError),
                          (((0, 0), {}, 0), TypeError),
                          (((0, 0), (0,), 0), TypeError),
                          (((0, 0), '', 0), TypeError),
                          (((0, 0), -1, 0), ValueError),
                          (((0, 0), 0x10000, 0), ValueError),
                          (((0, 0), 0, None), TypeError),
                          (((0, 0), 0, []), TypeError),
                          (((0, 0), 0, {}), TypeError),
                          (((0, 0), 0, .1), TypeError),
                          (((0, 0), 0, -1), ValueError),
                          (((0, 0), 0, 0x10000), ValueError),
                          (((0, 0), 0, ''), ValueError)]:
            with self.subTest(args=args):
                with self.assertRaises(exc):
                    dp = CircleDataPack(*args)

        dp = CircleDataPack((0, 0), 0, 0)
        self.assertEqual(len(bytes(dp)), len(dp))
        self.assertEqual(dp.xy, (0, 0))
        self.assertEqual(dp.radius, 0)
        self.assertEqual(dp.colour, 0)

        for xy, exc in [(None, TypeError),
                        ([], TypeError),
                        ({}, TypeError),
                        (.1, TypeError),
                        ('', TypeError),
                        ((0,), TypeError),
                        ((0, None), TypeError),
                        ((0, []), TypeError),
                        ((0, {}), TypeError),
                        ((0, .1), TypeError),
                        ((0, ''), TypeError),
                        ((0, -1), ValueError),
                        ((-1, 0), ValueError),
                        ((0, 0x10000), ValueError),
                        ((0x10000, 0), ValueError)]:
            with self.subTest(xy=xy):
                with self.assertRaises(exc):
                    dp.xy = xy

        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        for radius, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            ('', TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(radius=radius):
                with self.assertRaises(exc):
                    dp.radius = radius

        dp.radius = 13
        self.assertEqual(dp.radius, 13)

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (-1, ValueError),
                            (0x10000, ValueError),
                            ('', ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    dp.colour = colour

        dp.colour = 0x1234
        self.assertEqual(dp.colour, 0x1234)

    def test_PictureDataPack(self):

        dp = PictureDataPack(0, (0, 0), (0, 0), (0, 0))

        self.assertIs(type(dp.picid), int)
        self.assertEqual(dp.picid, 0)
        dp.picid = 1
        self.assertEqual(dp.picid, 1)

        self.assertIs(type(dp.xy_start), tuple)
        self.assertEqual(dp.xy_start, (0, 0))
        dp.xy_start = (1, 1)
        self.assertEqual(dp.xy_start, (1, 1))

        self.assertIs(type(dp.xy_end), tuple)
        self.assertEqual(dp.xy_end, (0, 0))
        dp.xy_end = (1, 1)
        self.assertEqual(dp.xy_end, (1, 1))

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertEqual(len(bytes(dp)), len(dp))

        for picid, exc in [(None, TypeError),
                           ('', TypeError),
                           ([], TypeError),
                           ({}, TypeError),
                           (.1, TypeError),
                           (-1, ValueError),
                           (0x10000, ValueError)]:
            with self.subTest(picid=picid):
                with self.assertRaises(exc):
                    _dp = PictureDataPack(picid, (0, 0), (0, 0), (0, 0))
                with self.assertRaises(exc):
                    dp.picid = picid

        for coords, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(coords=coords):
                with self.assertRaises(exc):
                    _dp = PictureDataPack(0, coords, (0, 0), (0, 0))
                with self.assertRaises(exc):
                    _dp = PictureDataPack(0, (0, 0), coords, (0, 0))
                with self.assertRaises(exc):
                    _dp = PictureDataPack(0, (0, 0), (0, 0), coords)
                with self.assertRaises(exc):
                    dp.xy_start = coords
                with self.assertRaises(exc):
                    dp.xy_end = coords
                with self.assertRaises(exc):
                    dp.xy = coords

    def test_IconDataPack(self):

        dp = IconDataPack((0, 0), 0)

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.iconid), int)
        self.assertEqual(dp.iconid, 0)
        dp.iconid = 1
        self.assertEqual(dp.iconid, 1)

        self.assertEqual(len(bytes(dp)), len(dp))

        for coords, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(coords=coords):
                with self.assertRaises(exc):
                    _dp = IconDataPack(coords, 0)
                with self.assertRaises(exc):
                    dp.xy = coords

        for iconid, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(iconid=iconid):
                with self.assertRaises(exc):
                    _dp = IconDataPack((0, 0), iconid)
                with self.assertRaises(exc):
                    dp.iconid = iconid

    def test_AreaFillDataPack(self):

        dp = AreaFillDataPack((0, 0), 0)

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)

        self.assertEqual(len(bytes(dp)), len(dp))

        for coords, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(coords=coords):
                with self.assertRaises(exc):
                    _dp = AreaFillDataPack(coords, 0)
                with self.assertRaises(exc):
                    dp.xy = coords

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = AreaFillDataPack((0, 0), colour)
                with self.assertRaises(exc):
                    dp.colour = colour

    def test_SpectrumDataPack(self):

        dp = SpectrumDataPack(0, 0, 0, 0)

        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)

        self.assertIs(type(dp.x), int)
        self.assertEqual(dp.x, 0)
        dp.x = 1
        self.assertEqual(dp.x, 1)

        self.assertIs(type(dp.y_start), int)
        self.assertEqual(dp.y_start, 0)
        dp.y_start = 1
        self.assertEqual(dp.y_start, 1)

        self.assertIs(type(dp.y_end), int)
        self.assertEqual(dp.y_end, 0)
        dp.y_end = 1
        self.assertEqual(dp.y_end, 1)

        self.assertEqual(len(bytes(dp)), len(dp))

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = SpectrumDataPack(colour, 0, 0, 0)
                with self.assertRaises(exc):
                    dp.colour = colour

        for v, exc in [(None, TypeError),
                       ('', TypeError),
                       ([], TypeError),
                       ({}, TypeError),
                       (.1, TypeError),
                       ((0,), TypeError),
                       ((0, 0), TypeError),
                       (-1, ValueError),
                       (0x10000, ValueError)]:
            with self.subTest(v=v):
                with self.assertRaises(exc):
                    _dp = SpectrumDataPack(0, v, 0, 0)
                with self.assertRaises(exc):
                    _dp = SpectrumDataPack(0, 0, v, 0)
                with self.assertRaises(exc):
                    _dp = SpectrumDataPack(0, 0, 0, v)
                with self.assertRaises(exc):
                    dp.x = v
                with self.assertRaises(exc):
                    dp.y_start = v
                with self.assertRaises(exc):
                    dp.y_end = v

    def test_SegmentDataPack(self):

        dp = SegmentDataPack(0, (0, 0), (0, 0))

        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)

        self.assertIs(type(dp.xy_start), tuple)
        self.assertEqual(dp.xy_start, (0, 0))
        dp.xy_start = (1, 1)
        self.assertEqual(dp.xy_start, (1, 1))

        self.assertIs(type(dp.xy_end), tuple)
        self.assertEqual(dp.xy_end, (0, 0))
        dp.xy_end = (1, 1)
        self.assertEqual(dp.xy_end, (1, 1))

        self.assertEqual(len(bytes(dp)), len(dp))

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = SegmentDataPack(colour, (0, 0), (0, 0))
                with self.assertRaises(exc):
                    dp.colour = colour

        for coords, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(coords=coords):
                with self.assertRaises(exc):
                    _dp = SegmentDataPack(0, coords, (0, 0))
                with self.assertRaises(exc):
                    _dp = SegmentDataPack(0, (0, 0), coords)
                with self.assertRaises(exc):
                    dp.xy_start = coords
                with self.assertRaises(exc):
                    dp.xy_end = coords

    def test_ArcDataPack(self):

        dp = ArcDataPack(0, (0, 0), 0, 0, 0)

        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.radius), int)
        self.assertEqual(dp.radius, 0)
        dp.radius = 1
        self.assertEqual(dp.radius, 1)

        self.assertIs(type(dp.angle_start), float)
        self.assertEqual(dp.angle_start, 0)
        dp.angle_start = 15
        self.assertEqual(dp.angle_start, 15)

        self.assertIs(type(dp.angle_end), float)
        self.assertEqual(dp.angle_end, 0)
        dp.angle_end = 15
        self.assertEqual(dp.angle_end, 15)

        self.assertEqual(len(bytes(dp)), len(dp))

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = ArcDataPack(colour, (0, 0), 0, 0, 0)
                with self.assertRaises(exc):
                    dp.colour = colour

        for coords, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(coords=coords):
                with self.assertRaises(exc):
                    _dp = ArcDataPack(0, coords, 0, 0, 0)
                with self.assertRaises(exc):
                    dp.xy = coords

        for v, exc in [(None, TypeError),
                       ('', TypeError),
                       ([], TypeError),
                       ({}, TypeError),
                       (.1, TypeError),
                       ((0,), TypeError),
                       ((0, 0), TypeError),
                       (-1, ValueError),
                       (0x10000, ValueError)]:
            with self.subTest(radius=v):
                with self.assertRaises(exc):
                    _dp = ArcDataPack(0, (0, 0), v, 0, 0)
                with self.assertRaises(exc):
                    dp.radius = v

        for angle, exc in [(None, TypeError),
                           ('', TypeError),
                           ([], TypeError),
                           ({}, TypeError),
                           (-1, ValueError),
                           (-0.1, ValueError),
                           (360.3, ValueError)]:
            with self.subTest(angle=angle):
                with self.assertRaises(exc):
                    _dp = ArcDataPack(0, (0, 0), 0, angle, 0)
                with self.assertRaises(exc):
                    _dp = ArcDataPack(0, (0, 0), 0, 0, angle)
                with self.assertRaises(exc):
                    dp.angle_start = angle
                with self.assertRaises(exc):
                    dp.angle_end = angle

    def test_CharacterDataPack(self):

        dp = CharacterDataPack(0, (0, 0), 0, 0, (0, 0), 0)

        self.assertIs(type(dp.colour), int)
        self.assertEqual(dp.colour, 0)
        dp.colour = 1
        self.assertEqual(dp.colour, 1)

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.libid), int)
        self.assertEqual(dp.libid, 0)
        dp.libid = 1
        self.assertEqual(dp.libid, 1)

        self.assertIs(type(dp.encoding), str)
        self.assertEqual(dp.encoding, '8bit')
        dp.encoding = 5
        self.assertEqual(dp.encoding, 'unicode')
        dp.encoding = '8bit'
        self.assertEqual(dp.encoding, '8bit')
        dp.encoding = 'cp1250'
        self.assertEqual(dp.encoding, 'cp1250')
        dp.encoding = ''
        with self.assertRaises(LookupError):
            bytes(dp)
        dp.encoding = 0

        self.assertIs(type(dp.size), tuple)
        self.assertEqual(dp.size, (0, 0))
        dp.size = (16, 32)
        self.assertEqual(dp.size, (16, 32))

        self.assertIs(type(dp.character), str)
        self.assertEqual(len(dp.character), 1)
        self.assertEqual(dp.character, '\0')
        dp.character = 'asd'
        self.assertEqual(dp.character, 'a')
        dp.character = 0x20
        self.assertEqual(dp.character, ' ')

        self.assertEqual(len(bytes(dp)), len(dp))

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = CharacterDataPack(colour, (0, 0), 0, 0, (0, 0), 0)
                with self.assertRaises(exc):
                    dp.colour = colour

        for v, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(v=v):
                with self.assertRaises(exc):
                    _dp = CharacterDataPack(0, v, 0, 0, (0, 0), 0)
                with self.assertRaises(exc):
                    _dp = CharacterDataPack(0, (0, 0), 0, 0, v, 0)
                with self.assertRaises(exc):
                    dp.xy = v
                with self.assertRaises(exc):
                    dp.size = v

        for libid, exc in [(None, TypeError),
                           ('', TypeError),
                           ([], TypeError),
                           ({}, TypeError),
                           (.1, TypeError),
                           ((0,), TypeError),
                           (-1, ValueError),
                           (256, ValueError)]:
            with self.subTest(libid=libid):
                with self.assertRaises(exc):
                    _dp = CharacterDataPack(0, (0, 0), libid, 0, (0, 0), 0)
                with self.assertRaises(exc):
                    dp.libid = libid

        for encoding, exc in [(None, TypeError),
                              ([], TypeError),
                              ({}, TypeError),
                              (.1, TypeError),
                              ((0,), TypeError),
                              (-1, ValueError),
                              (6, ValueError)]:
            with self.subTest(encoding=encoding):
                with self.assertRaises(exc):
                    _dp = CharacterDataPack(0, (0, 0), 0, encoding, (0, 0), 0)
                with self.assertRaises(exc):
                    dp.encoding = encoding

    def test_BicolorGraphDataPack(self):

        dp = BicolorGraphDataPack((0, 0), (0, 0), 0, 0)

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.size), tuple)
        self.assertEqual(dp.size, (0, 0))
        dp.size = (8, 8)
        self.assertEqual(dp.size, (8, 8))

        self.assertIs(type(dp.colour0), int)
        self.assertEqual(dp.colour0, 0)
        dp.colour0 = 1
        self.assertEqual(dp.colour0, 1)

        self.assertIs(type(dp.colour1), int)
        self.assertEqual(dp.colour1, 0)
        dp.colour1 = 1
        self.assertEqual(dp.colour1, 1)

        self.assertIs(type(dp.data), bytearray)
        self.assertEqual(len(dp.data), 0)
        dp.data = b'1234'
        self.assertEqual(len(dp.data), 4)
        for idx, v in enumerate(b'1234'):
            self.assertEqual(dp.data[idx], v)
            self.assertEqual(dp[idx], v)
        dp.data = b''
        for idx, v in enumerate(b'1234'):
            dp += v.to_bytes(1, 'big')
            self.assertEqual(len(dp.data), idx + 1)
            self.assertEqual(dp.data[idx], v)
            self.assertEqual(dp[-1], v)

        self.assertEqual(len(bytes(dp)), len(dp))

        for v, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(v=v):
                with self.assertRaises(exc):
                    _dp = BicolorGraphDataPack(v, (0, 0), 0, 0)
                with self.assertRaises(exc):
                    _dp = BicolorGraphDataPack((0, 0), v, 0, 0)
                with self.assertRaises(exc):
                    dp.xy = v
                with self.assertRaises(exc):
                    dp.size = v

        for colour, exc in [(None, TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            ('', ValueError),
                            (-1, ValueError),
                            (0x10000, ValueError)]:
            with self.subTest(colour=colour):
                with self.assertRaises(exc):
                    _dp = BicolorGraphDataPack((0, 0), (0, 0), colour, 0)
                with self.assertRaises(exc):
                    _dp = BicolorGraphDataPack((0, 0), (0, 0), 0, colour)
                with self.assertRaises(exc):
                    dp.colour0 = colour
                with self.assertRaises(exc):
                    dp.colour1 = colour

    def test_BitmapDataPack(self):

        dp = BitmapDataPack((0, 0), (0, 0))

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.size), tuple)
        self.assertEqual(dp.size, (0, 0))
        dp.size = (1, 1)
        self.assertEqual(dp.size, (1, 1))

        self.assertIs(type(dp.data), bytearray)
        self.assertEqual(len(dp.data), 0)
        dp.data = b'1234'
        self.assertEqual(len(dp.data), 4)
        for idx, v in enumerate(b'1234'):
            self.assertEqual(dp.data[idx], v)
            self.assertEqual(dp[idx], v)
        dp.data = b''
        for idx, v in enumerate(b'1234'):
            dp += v.to_bytes(1, 'big')
            self.assertEqual(len(dp.data), idx + 1)
            self.assertEqual(dp.data[idx], v)
            self.assertEqual(dp[-1], v)

        self.assertEqual(len(bytes(dp)), len(dp))

        for v, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(v=v):
                with self.assertRaises(exc):
                    _dp = BitmapDataPack(v, (0, 0))
                with self.assertRaises(exc):
                    _dp = BitmapDataPack((0, 0), v)
                with self.assertRaises(exc):
                    dp.xy = v
                with self.assertRaises(exc):
                    dp.size = v

    def test_DisplayZoomDataPack(self):

        dp = DisplayZoomDataPack((0, 0), (0, 0), (0, 0))

        self.assertIs(type(dp.xy), tuple)
        self.assertEqual(dp.xy, (0, 0))
        dp.xy = (1, 1)
        self.assertEqual(dp.xy, (1, 1))

        self.assertIs(type(dp.xy_start), tuple)
        self.assertEqual(dp.xy_start, (0, 0))
        dp.xy_start = (1, 1)
        self.assertEqual(dp.xy_start, (1, 1))

        self.assertIs(type(dp.xy_end), tuple)
        self.assertEqual(dp.xy_end, (0, 0))
        dp.xy_end = (1, 1)
        self.assertEqual(dp.xy_end, (1, 1))

        self.assertEqual(len(bytes(dp)), len(dp))

        for v, exc in [(None, TypeError),
                            ('', TypeError),
                            ([], TypeError),
                            ({}, TypeError),
                            (.1, TypeError),
                            ((0,), TypeError),
                            (('',), TypeError),
                            (([],), TypeError),
                            (({},), TypeError),
                            ((.1,), TypeError),
                            ((0, None), TypeError),
                            ((0, ''), TypeError),
                            ((0, []), TypeError),
                            ((0, {}), TypeError),
                            ((0, .1), TypeError),
                            ((0, 0, None), TypeError),
                            ((0, 0, ''), TypeError),
                            ((0, 0, []), TypeError),
                            ((0, 0, {}), TypeError),
                            ((0, 0, .1), TypeError),
                            ((-1, 0), ValueError),
                            ((0, -1), ValueError),
                            ((0x10000, 0), ValueError),
                            ((0, 0x10000), ValueError)]:
            with self.subTest(v=v):
                with self.assertRaises(exc):
                    _dp = DisplayZoomDataPack(v, (0, 0), (0, 0))
                with self.assertRaises(exc):
                    _dp = DisplayZoomDataPack((0, 0), v, (0, 0))
                with self.assertRaises(exc):
                    _dp = DisplayZoomDataPack((0, 0), (0, 0), v)
                with self.assertRaises(exc):
                    dp.xy = v
                with self.assertRaises(exc):
                    dp.xy_start = v
                with self.assertRaises(exc):
                    dp.xy_end = v
