import unittest
import struct
import sysfsgpio
import time
from apsbblib.apsbackbone import APSBackBone
from apsbblib.device_service.apsbb import common


class TestDevice(unittest.TestCase):

    DEVICE = None

    @classmethod
    def setUpClass(cls):
        cls.DEVICE = APSBackBone(port='/dev/ttyS1', baudrate=115200)
        cls.DEVICE.hardware_reset()

    @classmethod
    def tearDownClass(cls):
        dev = cls.DEVICE
        cls.DEVICE = None
        dev._xport._serial.close()
        del dev

    def test_pins(self):
        dev = TestDevice.DEVICE

        v = dev.intercom
        self.assertIs(type(v), sysfsgpio.Pin)
        with self.assertRaises(AttributeError):
            dev.intercom = None

        v = dev.breach
        self.assertIs(type(v), sysfsgpio.Pin)
        with self.assertRaises(AttributeError):
            dev.breach = None

        self.assertIs(type(dev.gpios), tuple)
        self.assertEqual(len(dev.gpios), 4)
        with self.assertRaises(AttributeError):
            dev.gpios = None
        for i in range(4):
            with self.subTest(i=i):
                self.assertIs(type(dev.gpios[i]), sysfsgpio.Pin)
                with self.assertRaises(TypeError):
                    dev.gpios[i] = None

    def test_pins_changed(self):
        dev = TestDevice.DEVICE

        v = dev.intercom_changed
        self.assertIs(type(v), sysfsgpio.Event)
        with self.assertRaises(AssertionError):
            dev.intercom_changed = None
        with self.assertRaises(TypeError):
            dev.intercom_changed += None

        v = dev.breach_changed
        self.assertIs(type(v), sysfsgpio.Event)
        with self.assertRaises(AssertionError):
            dev.breach_changed = None
        with self.assertRaises(TypeError):
            dev.breach_changed += None

    def test_events(self):
        dev = TestDevice.DEVICE

        for evt in [dev.barrier_event, dev.vehicle_event, dev.button_event]:
            with self.subTest(evt=evt):
                self.assertIs(type(evt), sysfsgpio.Event)
                with self.assertRaises(TypeError):
                    evt += None

        with self.assertRaises(AssertionError):
            dev.barrier_event = None
        with self.assertRaises(AssertionError):
            dev.vehicle_event = None
        with self.assertRaises(AssertionError):
            dev.button_event = None

    def test_sys(self):
        dev = TestDevice.DEVICE

        v = dev.sys_firmware_version()
        self.assertIs(type(v), dict)
        self.assertEqual(len(v), 5)
        for key in ['major', 'minor', 'maintenance', 'crc32', 'version']:
            self.assertIn(key, v)

        with self.assertRaises(ValueError):
            dev.sys_set_rtc('test')
        dev.sys_set_rtc()
        v = dev.sys_get_rtc()
        vv = time.time()
        self.assertIs(type(v), float)
        self.assertTrue(abs(vv - v) < 1)

        v = dev.sys_get_interrupt()
        self.assertIs(type(v), int)

    def test_btn(self):
        dev = TestDevice.DEVICE

        v = dev.btn_press_time()
        self.assertIs(type(v), int)

        for v in [dev.btn_is_pressed(), dev.btn_get_invert(), dev.btn_get_enabled()]:
            self.assertIs(type(v), bool)

        v = dev.btn_get_config()
        self.assertIs(type(v), tuple)
        for vv in v:
            self.assertIs(type(vv), bool)

        with self.assertRaises(ValueError):
            dev.btn_set_enabled(None)
        with self.assertRaises(ValueError):
            dev.btn_set_invert(None)

    def test_rgb(self):
        dev = TestDevice.DEVICE

        for v in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            dev.rgb_set_colour(common.Colour(v[0], v[1], v[2]))
            vv = dev.rgb_get_colour()
            self.assertIs(type(vv), common.Colour)
            self.assertEqual(vv.r, v[0])
            self.assertEqual(vv.g, v[1])
            self.assertEqual(vv.b, v[2])

        for v in [(-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
            with self.subTest(v=v):
                with self.assertRaises(struct.error):
                    dev.rgb_set_colour(common.Colour(v[0], v[1], v[2]))

        for v in [(100, 200, 25), (1000, 500, 1)]:
            dev.rgb_set_timings(common.Timings(v[0], v[1], v[2]))
            vv = dev.rgb_get_timings()
            self.assertIs(type(vv), common.Timings)
            self.assertEqual(vv.onTime, v[0])
            self.assertEqual(vv.offTime, v[1])
            self.assertEqual(vv.stepTime, v[2])

        for v in [(-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
            with self.subTest(v=v):
                with self.assertRaises(struct.error):
                    dev.rgb_set_timings(common.Timings(v[0], v[1], v[2]))

        for v in [common.LightMode.eLightOff,
                  common.LightMode.eLightOn,
                  common.LightMode.eLightPulsing]:
            dev.rgb_set_mode(v)
            vv = dev.rgb_get_mode()
            self.assertIs(type(vv), int)
            self.assertEqual(vv, v)

        with self.assertRaises(ValueError):
            dev.rgb_set_mode(None)
        with self.assertRaises(struct.error):
            dev.rgb_set_mode(-1)

        v = dev.rgb_get_coefficients()
        self.assertIs(type(v), common.Coefficients)

        v = dev.rgb_get_config()
        self.assertIs(type(v), tuple)
        self.assertEqual(len(v), 4)
        self.assertIs(type(v[0]), int)
        self.assertIs(type(v[1]), common.Timings)
        self.assertIs(type(v[2]), common.Colour)
        self.assertIs(type(v[3]), common.Coefficients)

    def test_path(self):
        dev = TestDevice.DEVICE

        v = dev.path_get_status()
        self.assertIs(type(v), common.PathStatus)

        for v in [0, 100]:
            for ff in [(dev.path_set_barrier_timeout, dev.path_get_barrier_timeout),
                       (dev.path_set_loops_timeout, dev.path_get_loops_timeout),
                       (dev.path_set_loops_hold, dev.path_get_loops_hold)]:
                ff[0](v)
                vv = ff[1]()
                self.assertIs(type(vv), int)
                self.assertEqual(vv, v)
                with self.assertRaises(struct.error):
                    ff[0](-1)
                with self.assertRaises(ValueError):
                    ff[0](None)

        v = dev.path_get_config()
        self.assertIs(type(v), tuple)
        self.assertEqual(len(v), 3)
        for vv in v:
            self.assertIs(type(vv), int)

    def test_buzzer(self):
        dev = TestDevice.DEVICE

        for v in [240, 480, 1440, 1920, 2300]:
            dev.buzzer_set_frequency(v)
            vv = dev.buzzer_get_frequency()
            self.assertIs(type(vv), int)
            self.assertTrue(vv >= (0.9 * v) and vv <= (1.1 * v))

        with self.assertRaises(ValueError):
            dev.buzzer_set_frequency(None)
        with self.assertRaises(struct.error):
            dev.buzzer_set_frequency(-1)
