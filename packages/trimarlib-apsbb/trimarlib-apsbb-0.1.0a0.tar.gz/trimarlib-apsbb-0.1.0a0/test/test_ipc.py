import struct
import time
import unittest
from apsbblib.server import Server
from apsbblib.client import Client
from apsbblib.system_service.apsbbsys import common


class TestInterProcessComms(unittest.TestCase):

    SERVER = None

    @classmethod
    def setUpClass(cls):
        cls.SERVER = Server(port='/dev/ttyS1', baudrate=115200)
        cls.SERVER.start()
        cls.SOCKET_PATH = cls.SERVER.socket_path
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.SERVER.stop()
        cls.SERVER = None

    def setUp(self):
        self.CLIENT = Client(path=self.SOCKET_PATH)
        self.CLIENT.open()

    def tearDown(self):
        self.CLIENT.close()
        self.CLIENT = None

    def test_singleton(self):
        with self.assertRaises(RuntimeError):
            server = Server(port='/dev/ttyS1', baudrate=115200)
            server.start()

    def test_open(self):
        with self.assertRaises(RuntimeError):
            self.CLIENT.open()

    def test_callbacks(self):
        for v in [self.CLIENT.button_changed_callback,
                  self.CLIENT.vehicle_changed_callback,
                  self.CLIENT.barrier_changed_callback,
                  self.CLIENT.intercom_changed_callback,
                  self.CLIENT.breach_changed_callback,
                  self.CLIENT.gpio_changed_callback]:
            self.assertIsNone(v)

        def callback(*args, **kwargs):
            pass

        self.CLIENT.button_changed_callback = callback
        self.CLIENT.vehicle_changed_callback = callback
        self.CLIENT.barrier_changed_callback = callback
        self.CLIENT.intercom_changed_callback = callback
        self.CLIENT.breach_changed_callback = callback
        self.CLIENT.gpio_changed_callback = callback

        for v in [self.CLIENT.button_changed_callback,
                  self.CLIENT.vehicle_changed_callback,
                  self.CLIENT.barrier_changed_callback,
                  self.CLIENT.intercom_changed_callback,
                  self.CLIENT.breach_changed_callback,
                  self.CLIENT.gpio_changed_callback]:
            self.assertEqual(v, callback)

        self.CLIENT.button_changed_callback = None
        self.CLIENT.vehicle_changed_callback = None
        self.CLIENT.barrier_changed_callback = None
        self.CLIENT.intercom_changed_callback = None
        self.CLIENT.breach_changed_callback = None
        self.CLIENT.gpio_changed_callback = None

    def test_sys(self):
        with Client(path=self.SOCKET_PATH) as c:
            for obj in [self.CLIENT, c]:
                obj.firmware_version()
                obj.software_reset()
                obj.hardware_reset()

        c = Client(path=self.SOCKET_PATH)
        with self.assertRaises(AttributeError):
            c.firmware_version()
        with self.assertRaises(AttributeError):
            c.software_reset()
        with self.assertRaises(AttributeError):
            c.hardware_reset()

    def test_button(self):
        self.assertIs(type(self.CLIENT.button_is_pressed()), bool)
        self.assertIs(type(self.CLIENT.button_press_time()), int)

        for ff in [(self.CLIENT.button_set_enabled, self.CLIENT.button_get_enabled),
                   (self.CLIENT.button_set_invert, self.CLIENT.button_get_invert)]:
            with self.assertRaises(ValueError):
                ff[0](None)
            ff[0](True)
            vv = ff[1]()
            self.assertIs(type(vv), bool)
            self.assertTrue(vv)
            ff[0](False)
            vv = ff[1]()
            self.assertIs(type(vv), bool)
            self.assertFalse(vv)

        args = (True, False)
        with self.assertRaises(ValueError):
            self.CLIENT.button_set_config(None, None)
        self.CLIENT.button_set_config(*args)
        vv = self.CLIENT.button_get_config()
        self.assertEqual(len(args), len(vv))
        self.assertEqual(args[0], vv[0])
        self.assertEqual(args[1], vv[1])

    def test_rgb(self):
        c = self.CLIENT

        for v in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            c.rgb_set_colour(common.Colour(v[0], v[1], v[2]))
            vv = c.rgb_get_colour()
            self.assertIs(type(vv), common.Colour)
            self.assertEqual(vv.r, v[0])
            self.assertEqual(vv.g, v[1])
            self.assertEqual(vv.b, v[2])

        for v in [(-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
            with self.subTest(v=v):
                with self.assertRaises(struct.error):
                    c.rgb_set_colour(common.Colour(v[0], v[1], v[2]))

        for v in [(100, 200, 25), (1000, 500, 1)]:
            c.rgb_set_timings(common.Timings(v[0], v[1], v[2]))
            vv = c.rgb_get_timings()
            self.assertIs(type(vv), common.Timings)
            self.assertEqual(vv.onTime, v[0])
            self.assertEqual(vv.offTime, v[1])
            self.assertEqual(vv.stepTime, v[2])

        for v in [(-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
            with self.subTest(v=v):
                with self.assertRaises(struct.error):
                    c.rgb_set_timings(common.Timings(v[0], v[1], v[2]))

        for v in [common.LightMode.eLightOff,
                  common.LightMode.eLightOn,
                  common.LightMode.eLightPulsing]:
            c.rgb_set_mode(v)
            vv = c.rgb_get_mode()
            self.assertIs(type(vv), int)
            self.assertEqual(vv, v)

        with self.assertRaises(ValueError):
            c.rgb_set_mode(None)
        with self.assertRaises(struct.error):
            c.rgb_set_mode(-1)

        v = c.rgb_get_coefficients()
        self.assertIs(type(v), common.Coefficients)

        v = c.rgb_get_config()
        self.assertIs(type(v), tuple)
        self.assertEqual(len(v), 4)
        self.assertIs(type(v[0]), int)
        self.assertIs(type(v[1]), common.Timings)
        self.assertIs(type(v[2]), common.Colour)
        self.assertIs(type(v[3]), common.Coefficients)
