import erpc
import errno
import logging
import os
import socket
import threading
from functools import wraps
from .apsbackbone import APSBackBone
from .transport import SocketTransport
from .system_service import ERPC_GENERATED_SHIM_CODE_CRC, apsbbsys

_logger = logging.getLogger('.'.join(['apsbblib', __name__]))
RUNTIME_DIR = '/run/apsbblib'
SOCKET_NAME = 'apsbbserver.sock'
PID_NAME = 'apsbbserver.pid'


class DeviceHandler(apsbbsys.interface.IDevice):
    def __init__(self, device):
        self._device = device
        self._lock = threading.Lock()

    def _sync(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            with self._lock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn

    @_sync
    def firmware_version(self):
        dd = self._device.sys_firmware_version()
        ret = apsbbsys.common.FirmwareVersion()
        ret.major = dd['major']
        ret.minor = dd['minor']
        ret.maintenance = dd['maintenance']
        ret.crc32 = dd['crc32']
        ret.sversion = dd['version']
        return ret

    @_sync
    def software_reset(self):
        self._device.sys_reset()

    @_sync
    def hardware_reset(self):
        self._device.hardware_reset()

    @_sync
    def btn_is_pressed(self):
        return self._device.btn_is_pressed()

    @_sync
    def btn_press_time(self):
        return self._device.btn_press_time()

    @_sync
    def btn_set_invert(self, enable):
        self._device.btn_set_invert(enable)

    @_sync
    def btn_get_invert(self):
        return self._device.btn_get_invert()

    @_sync
    def btn_set_enabled(self, enable):
        self._device.btn_set_enabled(enable)

    @_sync
    def btn_get_enabled(self):
        return self._device.btn_get_enabled()

    @_sync
    def btn_set_config(self, enable, invert):
        self._device.btn_set_config(enable, invert)

    @_sync
    def btn_get_config(self, enable, invert):
        enable.value, invert.value = self._device.btn_get_config()

    @_sync
    def rgb_set_colour(self, colour):
        self._device.rgb_set_colour(colour)

    @_sync
    def rgb_get_colour(self, colour):
        colour.value = self._device.rgb_get_colour()

    @_sync
    def rgb_set_timings(self, timings):
        self._device.rgb_set_timings(timings)

    @_sync
    def rgb_get_timings(self, timings):
        timings.value = self._device.rgb_get_timings()

    @_sync
    def rgb_set_mode(self, mode):
        self._device.rgb_set_mode(mode)

    @_sync
    def rgb_get_mode(self):
        return self._device.rgb_get_mode()

    @_sync
    def rgb_set_coefficients(self, coeffs):
        self._device.rgb_set_coefficients(coeffs)

    @_sync
    def rgb_get_coefficients(self, coeffs):
        coeffs.value = self._device.rgb_get_coefficients()

    @_sync
    def rgb_set_config(self, mode, timings, colour, coeffs):
        self._device.rgb_set_config(mode, timings, colour, coeffs)

    @_sync
    def rgb_get_config(self, mode, timings, colour, coeffs):
        mode.value, timings.value, colour.value, coeffs.value = self._device.rgb_get_config()

    @_sync
    def path_get_status(self, status):
        status.value = self._device.path_get_status()

    @_sync
    def path_open(self, force, autoClose):
        self._device.path_open(force, autoClose)

    @_sync
    def path_close(self):
        self._device.path_close()

    @_sync
    def path_set_barrier_timeout(self, timeout):
        self._device.path_set_barrier_timeout(timeout)

    @_sync
    def path_get_barrier_timeout(self):
        return self._device.path_get_barrier_timeout()

    @_sync
    def path_set_loops_timeout(self, timeout):
        self._device.path_set_loops_timeout(timeout)

    @_sync
    def path_get_loops_timeout(self):
        return self._device.path_get_loops_timeout()

    @_sync
    def path_set_loops_hold(self, time):
        self._device.path_set_loops_hold(time)

    @_sync
    def path_get_loops_hold(self):
        return self._device.path_get_loops_hold()

    @_sync
    def path_get_result(self):
        return self._device.path_get_result()

    @_sync
    def path_clear_result(self):
        self._device.path_clear_result()

    @_sync
    def path_set_config(self, barrier_timeout, loops_timeout, loops_hold):
        self._device.path_set_config(barrier_timeout, loops_timeout, loops_hold)

    @_sync
    def path_get_config(self, barrier_timeout, loops_timeout, loops_hold):
        barrier_timeout.value, loops_timeout.value, loops_hold.value = self._device.path_get_config()

    @_sync
    def buzzer_set_frequency(self, frequency):
        self._device.buzzer_set_frequency(frequency)

    @_sync
    def buzzer_get_frequency(self):
        return self._device.buzzer_get_frequency()

    @_sync
    def buzzer_enable(self, onTime, offTime, repeat):
        self._device.buzzer_enable(onTime, offTime, repeat)

    @_sync
    def buzzer_enable_ACK(self):
        self._device.buzzer_enable_ACK()

    @_sync
    def buzzer_enable_NAK(self):
        self._device.buzzer_enable_NAK()

    @_sync
    def icom_get(self):
        return self._device.intercom.value

    @_sync
    def icom_set_active_low(self, active_low):
        self._device.intercom.invert = active_low

    @_sync
    def icom_get_active_low(self):
        return self._device.intercom.invert

    @_sync
    def breach_get(self):
        return self._device.breach.value

    @_sync
    def breach_set_active_low(self, active_low):
        self._device.breach.invert = active_low

    @_sync
    def breach_get_active_low(self):
        return self._device.breach.invert

    @_sync
    def gpio_get(self, idx):
        return self._device.gpios[idx].value

    @_sync
    def gpio_set(self, idx, enable):
        try:
            self._device.gpios[idx].value = enable
        except RuntimeError:
            pass

    @_sync
    def gpio_set_direction(self, idx, direction):
        if direction == apsbbsys.common.PinDirection.ePinInput:
            self._device.gpios[idx].direction = 'in'
        else:
            self._device.gpios[idx].direction = 'out'

    @_sync
    def gpio_get_direction(self, idx):
        return self._device.gpios[idx].direction

    @_sync
    def gpio_set_active_low(self, idx, active_low):
        self._device.gpios[idx].invert = active_low

    @_sync
    def gpio_get_active_low(self, idx):
        return self._device.gpios[idx].invert


class Server(object):
    def __init__(self, *, port=None, baudrate=None, firmware=None):
        self._device = None
        self._device_args = (port, baudrate, firmware)
        self._cancel = threading.Event()
        self._handler = None
        self._service = None
        self._clients = []
        self._clients_lock = threading.Lock()
        self._thread = None
        self._thread_lock = threading.Lock()

    @property
    def socket_path(self):
        return self._sock_path

    def _listener(self):
        _logger.info('started')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(.5)
        sock.bind(self._sock_path)
        sock.listen()
        processor_threads = []
        processor_idx = 0

        while not self._cancel.is_set():
            try:
                nsock, _ = sock.accept()
            except socket.timeout:
                nsock = None

            if nsock is not None:
                _logger.debug('accepted new connection')
                nm = 'processor-{}'.format(processor_idx)
                processor_idx += 1
                th = threading.Thread(name=nm, target=self._processor, args=(nsock,))
                processor_threads.append(th)
                th.start()
                del nm

            dead_threads = []
            for th in processor_threads:
                if not th.is_alive():
                    dead_threads.append(th)
            if len(dead_threads) > 0:
                _logger.debug('joining %d dead threads', len(dead_threads))
                for th in dead_threads:
                    th.join()
                    processor_threads.remove(th)
            del dead_threads

        _logger.debug('cancellation requested')
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        del sock
        os.unlink(self._sock_path)
        for th in processor_threads:
            th.join()
        _logger.info('returning')
        return

    def _processor_server(self, srvr):
        _logger.info('started')
        try:
            srvr.run()
        except erpc.transport.ConnectionClosed:
            _logger.info('connection closed')
        except:
            _logger.exception('exception while running erpc server')
        _logger.info('returning')
        return

    def _processor(self, sock):
        _logger.info('started')
        xport = SocketTransport(sock)
        xport.crc_16 = ERPC_GENERATED_SHIM_CODE_CRC
        arbitrator = erpc.arbitrator.TransportArbitrator(xport,
                                                         erpc.basic_codec.BasicCodec())
        manager = erpc.client.ClientManager(xport,
                                            erpc.basic_codec.BasicCodec)
        manager.arbitrator = arbitrator
        c = apsbbsys.client.ClientClient(manager)
        with self._clients_lock:
            self._clients.append(c)

        s = erpc.simple_server.SimpleServer(arbitrator, erpc.basic_codec.BasicCodec)
        s.add_service(self._service)
        sth = threading.Thread(target=self._processor_server,
                               args=(s,),
                               name=('{}-erpc-server'.format(threading.current_thread().name)))
        sth.start()

        self._cancel.wait()
        _logger.debug('cancellation requested')

        s.stop()
        sock.shutdown(socket.SHUT_RDWR)
        sth.join()
        with self._clients_lock:
            self._clients.remove(c)
        sock.close()

        _logger.info('returning')
        return

    def _intercom_changed_handler(self, pin, value):
        _logger.debug('dispatching notification')
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.icom_changed(value)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _breach_changed_handler(self, pin, value):
        _logger.debug('dispatching breach changed notification')
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.breach_changed(value)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _gpio_changed_handler(self, pin, value):
        idx = None
        for i in range(len(self._device.gpios)):
            if pin == self._device.gpios[i]:
                idx = i
                break
        if idx is None:
            _logger.error('failed to identify gpio pin, notification dispatching aborted')
            return
        _logger.debug('dispatching notification, gpio[%d] ', idx)
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.gpio_changed(idx, value)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _button_changed_handler(self, value):
        _logger.debug('dispatching notification')
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.button_changed(value)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _vehicle_changed_handler(self, status):
        _logger.debug('dispatching notification')
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.vehicle_changed(status)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _barrier_changed_handler(self, status):
        _logger.debug('dispatching notification')
        with self._clients_lock:
            for c in self._clients:
                try:
                    c.barrier_changed(status)
                except:
                    _logger.exception('failed to dispatch notification to client: %s', c)

    def _runtime_setUp(self):
        try:
            os.stat(RUNTIME_DIR)
            self._pid_path = '/'.join([RUNTIME_DIR, PID_NAME])
            self._sock_path = '/'.join([RUNTIME_DIR, SOCKET_NAME])
        except FileNotFoundError:
            path = os.getcwd()
            _logger.warning('runtime directory %s not found, using current directory (%s)', RUNTIME_DIR, path)
            self._pid_path = '/'.join([path, PID_NAME])
            self._sock_path = '/'.join([path, SOCKET_NAME])
        try:
            with open(self._pid_path, 'r') as fd:
                pid = fd.read().strip()
                msg = 'another server instance is already running (PID={})'.format(pid)
                raise RuntimeError(msg)
        except FileNotFoundError:
            pass
        with open(self._pid_path, 'w') as fd:
            fd.write(str(os.getpid()))
            fd.write('\n')
        try:
            self._device = APSBackBone(*self._device_args)
        except:
            self._runtime_tearDown()
            raise
        self._device.intercom_changed += self._intercom_changed_handler
        self._device.breach_changed += self._breach_changed_handler
        for gpio in self._device.gpios:
            gpio.input_changed += self._gpio_changed_handler
        self._device.barrier_event += self._barrier_changed_handler
        self._device.vehicle_event += self._vehicle_changed_handler
        self._device.button_event += self._button_changed_handler

        self._handler = DeviceHandler(self._device)
        self._service = apsbbsys.server.DeviceService(self._handler)

    def _runtime_tearDown(self):
        self._service = None
        self._handler = None
        self._device = None
        # unlink PID file
        os.unlink(self._pid_path)

    def start(self):
        with self._thread_lock:
            if self._thread is not None:
                raise RuntimeError('server thread already created')
            self._runtime_setUp()
            self._thread = threading.Thread(target=self._listener, name='listener')
            self._thread.start()

    def stop(self):
        with self._thread_lock:
            if self._thread is None:
                return
            self._cancel.set()
            self._thread.join()
            self._thread = None
            self._cancel.clear()
            self._runtime_tearDown()
