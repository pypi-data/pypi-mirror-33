
from .device_service import ERPC_GENERATED_SHIM_CODE_CRC
from .device_service.apsbb import common, client

import erpc
import logging
import threading
import queue
import time
import serial
import socket
import errno
import sysfsgpio
import struct
from functools import wraps

_logger = logging.getLogger(__name__)


class APSBackBone(object):
    def __init__(self, port, baudrate, firmware=None):
        self._xport = erpc.transport.SerialTransport(port, baudrate, timeout=5)
        self._xport.crc_16 = ERPC_GENERATED_SHIM_CODE_CRC
        self._xport_rlock = threading.RLock()
        self._manager = erpc.client.ClientManager(self._xport, erpc.basic_codec.BasicCodec)
        self._sys_client = client.SystemClient(self._manager)
        self._rgb_client = client.RGBClient(self._manager)
        self._path_client = client.PathClient(self._manager)
        self._btn_client = client.ButtonClient(self._manager)
        self._buzz_client = client.BuzzerClient(self._manager)

        self._boot_pin = sysfsgpio.Pin('PA7', 'out')
        self._rst_pin = sysfsgpio.Pin('PA8', 'out')
        self._irq_pin = sysfsgpio.Pin('PA9')
        self._icom_pin = sysfsgpio.Pin('PC7')
        self._breach_pin = sysfsgpio.Pin('PD14')
        self._gpios = (sysfsgpio.Pin('PA10'),
                       sysfsgpio.Pin('PA20'),
                       sysfsgpio.Pin('PA21'),
                       sysfsgpio.Pin('PC4'))

        self._event_rlock = threading.RLock()

        self._irq_pin.input_changed += self._irq_pin_callback
        self._irq_pin.enabled = True

        self._event_vehicle = sysfsgpio.Event()
        self._event_barrier = sysfsgpio.Event()
        self._event_button = sysfsgpio.Event()

        self._icom_pin.enabled = True
        self._breach_pin.enabled = True

        self._dispatcher_event = threading.Event()
        self._dispatcher_event.set()
        self._dispatcher_thread = threading.Thread(
            name='dispatcher',
            target=self._dispatcher_fun,
            daemon=True)
        self._dispatcher_thread.start()

    def _sync_xport(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            with self._xport_rlock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn

    def _sync_event(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            with self._event_rlock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn

    def _irq_pin_callback(self, pin, v):
        if pin == self._irq_pin:
            if v == 0:
                _logger.debug('new interrupt from the backbone')
                self._dispatcher_event.set()
            else:
                _logger.debug('backbone interrupt line cleared')
        elif pin != self._irq_pin:
            _logger.warning('callback from unexpected source: %s, %d',
                            pin.pinname(),
                            v)

    def _dispatcher_fun(self):
        _logger.debug('started')
        path_status = None
        button_pressed = None
        while True:
            if self._dispatcher_event.wait(.5):
                self._dispatcher_event.clear()
            with self._xport_rlock:
                try:
                    irq = self.sys_get_interrupt()
                except (struct.error, erpc.client.RequestError) as e:
                    _logger.exception('failed to read interrupt register: %s', e, exc_info=False)
                    self._xport._serial.flushInput()
                    continue
                except serial.SerialException:
                    _logger.exception('serial port error', exc_info=False)
                    return
                if irq != 0:
                    _logger.debug('got event, irq=%d', irq)
                    if (irq & (common.InterruptBits.eIntBarrier
                               | common.InterruptBits.eIntVehicle)) != 0:
                        path_status = self.path_get_status()
                        self.path_clear_result()
                        _logger.debug('new path status is %s', path_status)
                    if (irq & common.InterruptBits.eIntButton) != 0:
                        button_pressed = self.btn_is_pressed()
                        _logger.debug('new button status is %s', button_pressed)
                self.sys_clear_interrupt(irq)

            with self._event_rlock:
                if (irq & common.InterruptBits.eIntBarrier) != 0:
                    _logger.debug('dispatching barrier event')
                    self._event_barrier(path_status)
                if (irq & common.InterruptBits.eIntVehicle) != 0:
                    _logger.debug('dispatching vehicle event')
                    self._event_vehicle(path_status)
                if (irq & common.InterruptBits.eIntButton) != 0:
                    _logger.debug('dispatching button event')
                    self._event_button(button_pressed)

    @property
    def intercom(self):
        """Getter of the underlying Pin object"""
        return self._icom_pin

    @property
    def intercom_changed(self):
        """Proxy property wrapper around underlying Pin object callback"""
        return self._icom_pin.input_changed

    @intercom_changed.setter
    @_sync_event
    def intercom_changed(self, v):
        assert type(v) is sysfsgpio.Event, 'assigned object type mismatch'
        self._icom_pin.input_changed = v

    @property
    def breach(self):
        """Getter of the underlying Pin object"""
        return self._breach_pin

    @property
    def breach_changed(self):
        """Proxy property wrapper around underlying Pin object callback"""
        return self._breach_pin.input_changed

    @breach_changed.setter
    @_sync_event
    def breach_changed(self, v):
        assert type(v) is sysfsgpio.Event, 'assigned object type mismatch'
        self._breach_pin.input_changed = v

    @property
    def barrier_event(self):
        return self._event_barrier

    @barrier_event.setter
    @_sync_event
    def barrier_event(self, value):
        assert type(value) is sysfsgpio.Event, 'assigned object type mismatch'
        self._event_barrier = value

    @property
    def vehicle_event(self):
        return self._event_vehicle

    @vehicle_event.setter
    @_sync_event
    def vehicle_event(self, value):
        assert type(value) is sysfsgpio.Event, 'assigned object type mismatch'
        self._event_vehicle = value

    @property
    def button_event(self):
        return self._event_button

    @button_event.setter
    @_sync_event
    def button_event(self, value):
        assert type(value) is sysfsgpio.Event, 'assigned object type mismatch'
        self._event_button = value

    @property
    def gpios(self):
        return self._gpios

    @_sync_xport
    def hardware_reset(self):
        """Hardware reset of the backbone

        Asserts board reset signal, holds it for .5s, deasserts and
        waits 1s for boot to complete."""
        self._rst_pin.value = 1
        time.sleep(.5)
        self._rst_pin.value = 0
        time.sleep(1)

    @_sync_xport
    def sys_firmware_version(self):
        major = erpc.Reference()
        minor = erpc.Reference()
        maintenance = erpc.Reference()
        crc = erpc.Reference()
        ver = self._sys_client.sys_firmware_version(major, minor, maintenance, crc)
        ret = dict(version=ver,
                   major=major.value,
                   minor=minor.value,
                   maintenance=maintenance.value,
                   crc32=crc.value)
        return ret

    @_sync_xport
    def sys_reset(self):
        self._sys_client.sys_reset()
        time.sleep(1)
        return

    @_sync_xport
    def sys_bootloader(self):
        self._sys_client.sys_bootloader()
        return

    @_sync_xport
    def sys_set_rtc(self, seconds=None):
        if seconds is None:
            seconds = time.time()
        self._sys_client.sys_set_rtc(common.Timeval(int(seconds), 0))
        return

    @_sync_xport
    def sys_get_rtc(self):
        tv = erpc.Reference()
        self._sys_client.sys_get_rtc(tv)
        ret = tv.value.secs + tv.value.usecs / 1e6
        return ret

    @_sync_xport
    def sys_get_interrupt(self):
        return self._sys_client.sys_get_interrupt()

    @_sync_xport
    def sys_clear_interrupt(self, mask=common.InterruptBits.eIntAll):
        self._sys_client.sys_clear_interrupt(mask)
        return

    @_sync_xport
    def btn_is_pressed(self):
        return self._btn_client.btn_is_pressed()

    @_sync_xport
    def btn_press_time(self):
        return self._btn_client.btn_press_time()

    @_sync_xport
    def btn_set_invert(self, enable):
        self._btn_client.btn_set_invert(enable)

    @_sync_xport
    def btn_get_invert(self):
        return self._btn_client.btn_get_invert()

    @_sync_xport
    def btn_set_enabled(self, enable):
        self._btn_client.btn_set_enabled(enable)

    @_sync_xport
    def btn_get_enabled(self):
        return self._btn_client.btn_get_enabled()

    @_sync_xport
    def btn_set_config(self, enable, invert):
        self._btn_client.btn_set_config(enable, invert)

    @_sync_xport
    def btn_get_config(self):
        enable = erpc.Reference()
        invert = erpc.Reference()
        self._btn_client.btn_get_config(enable, invert)
        return (enable.value, invert.value)

    @_sync_xport
    def rgb_set_colour(self, colour):
        self._rgb_client.rgb_set_colour(colour)

    @_sync_xport
    def rgb_get_colour(self):
        colour = erpc.Reference()
        self._rgb_client.rgb_get_colour(colour)
        return colour.value

    @_sync_xport
    def rgb_set_timings(self, timings):
        self._rgb_client.rgb_set_timings(timings)

    @_sync_xport
    def rgb_get_timings(self):
        timings = erpc.Reference()
        self._rgb_client.rgb_get_timings(timings)
        return timings.value

    @_sync_xport
    def rgb_set_mode(self, mode):
        self._rgb_client.rgb_set_mode(mode)

    @_sync_xport
    def rgb_get_mode(self):
        return self._rgb_client.rgb_get_mode()

    @_sync_xport
    def rgb_set_coefficients(self, coeffs):
        self._rgb_client.rgb_set_coefficients(coeffs)

    @_sync_xport
    def rgb_get_coefficients(self):
        coeffs = erpc.Reference()
        self._rgb_client.rgb_get_coefficients(coeffs)
        return coeffs.value

    @_sync_xport
    def rgb_set_config(self, mode, timings, colour, coeffs):
        self._rgb_client.rgb_set_config(mode, timings, colour, coeffs)

    @_sync_xport
    def rgb_get_config(self):
        mode = erpc.Reference()
        timings = erpc.Reference()
        colour = erpc.Reference()
        coeffs = erpc.Reference()
        self._rgb_client.rgb_get_config(mode, timings, colour, coeffs)
        return (mode.value, timings.value, colour.value, coeffs.value)

    @_sync_xport
    def path_get_status(self):
        status = erpc.Reference()
        self._path_client.path_get_status(status)
        return status.value

    @_sync_xport
    def path_open(self, force=False, auto_close=True):
        self._path_client.path_open(force, auto_close)

    @_sync_xport
    def path_close(self):
        self._path_client.path_close()

    @_sync_xport
    def path_set_barrier_timeout(self, timeout):
        self._path_client.path_set_barrier_timeout(timeout)

    @_sync_xport
    def path_get_barrier_timeout(self):
        return self._path_client.path_get_barrier_timeout()

    @_sync_xport
    def path_set_loops_timeout(self, timeout):
        self._path_client.path_set_loops_timeout(timeout)

    @_sync_xport
    def path_get_loops_timeout(self):
        return self._path_client.path_get_loops_timeout()

    @_sync_xport
    def path_set_loops_hold(self, time):
        self._path_client.path_set_loops_hold(time)

    @_sync_xport
    def path_get_loops_hold(self):
        return self._path_client.path_get_loops_hold()

    @_sync_xport
    def path_get_result(self):
        return self._path_client.path_get_result()

    @_sync_xport
    def path_clear_result(self):
        self._path_client.path_clear_result()

    @_sync_xport
    def path_set_config(self, barrier_timeout, loops_timeout, loops_hold):
        self._path_client.path_set_config(barrier_timeout,
                                          loops_timeout,
                                          loops_hold)

    @_sync_xport
    def path_get_config(self):
        barrier_timeout = erpc.Reference()
        loops_timeout = erpc.Reference()
        loops_hold = erpc.Reference()
        self._path_client.path_get_config(barrier_timeout,
                                          loops_timeout,
                                          loops_hold)
        return (barrier_timeout.value,
                loops_timeout.value,
                loops_hold.value)

    @_sync_xport
    def buzzer_set_frequency(self, frequency):
        self._buzz_client.buzzer_set_frequency(frequency)

    @_sync_xport
    def buzzer_get_frequency(self):
        return self._buzz_client.buzzer_get_frequency()

    @_sync_xport
    def buzzer_enable(self, onTime, offTime, repeat):
        self._buzz_client.buzzer_enable(onTime, offTime, repeat)

    @_sync_xport
    def buzzer_enable_ACK(self):
        self._buzz_client.buzzer_enable_ACK()

    @_sync_xport
    def buzzer_enable_NAK(self):
        self._buzz_client.buzzer_enable_NAK()
