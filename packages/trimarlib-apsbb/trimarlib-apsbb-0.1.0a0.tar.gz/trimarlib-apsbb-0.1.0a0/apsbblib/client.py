import erpc
import logging
import socket
import threading
from functools import wraps
from .server import RUNTIME_DIR, SOCKET_NAME
from .transport import SocketTransport
from .system_service import ERPC_GENERATED_SHIM_CODE_CRC, apsbbsys
from .system_service.apsbbsys.common import LightMode
from .system_service.apsbbsys.common import BarrierPosition, BarrierAction
from .system_service.apsbbsys.common import VehiclePosition, TrackerResult
from .system_service.apsbbsys.common import PinDirection
from .system_service.apsbbsys.common import FirmwareVersion
from .system_service.apsbbsys.common import Colour
from .system_service.apsbbsys.common import Timings
from .system_service.apsbbsys.common import Coefficients
from .system_service.apsbbsys.common import PathStatus

_logger = logging.getLogger('.'.join(['apsbblib', __name__]))


def _locked(lock_name):
    def _decorator(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            lock = self.__getattribute__(lock_name)
            with lock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn
    return _decorator


class ClientHandler(apsbbsys.interface.IClient):
    def __init__(self):
        self._button_changed_callback = None
        self._vehicle_changed_callback = None
        self._barrier_changed_callback = None
        self._icom_changed_callback = None
        self._breach_changed_callback = None
        self._gpio_changed_callback = None
        self._lock = threading.Lock()
        pass

    def _sync(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            with self._lock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn

    @_locked('_lock')
    def button_changed(self, pressed):
        if self._button_changed_handler is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._button_changed_callback(pressed)
        except:
            _logger.exception('exception while invoking callback')

    @_locked('_lock')
    def vehicle_changed(self, status):
        if self._vehicle_changed_callback is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._vehicle_changed_callback(status)
        except:
            _logger.exception('exception while invoking callback')

    @_locked('_lock')
    def barrier_changed(self, status):
        if self._barrier_changed_callback is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._barrier_changed_callback(status)
        except:
            _logger.exception('exception while invoking callback')

    @_locked('_lock')
    def icom_changed(self, active):
        if self._icom_changed_callback is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._icom_changed_callback(active)
        except:
            _logger.exception('exception while invoking callback')

    @_locked('_lock')
    def breach_changed(self, active):
        if self._breach_changed_callback is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._breach_changed_callback(active)
        except:
            _logger.exception('exception while invoking callback')

    @_locked('_lock')
    def gpio_changed(self, idx, active):
        if self._gpio_changed_callback is None:
            _logger.info('no callback to invoke')
            return
        try:
            self._gpio_changed_callback(idx, active)
        except:
            _logger.exception('exception while invoking callback')


class Client(object):
    """Client of the IPC server.

    TODO
    """

    def __init__(self, *, path=None):
        """Initializes client object.

        Parameters
        ----------
        path : str
            Path to the UNIX socket created by the server object. Defaults
            to the path used by server when run as system daemon.
        """
        if path is None:
            path = '/'.join([RUNTIME_DIR, SOCKET_NAME])
        self._sock_path = path

        self._sock = None
        self._xport = None
        self._xport_rlock = threading.RLock()
        self._arbitrator = None
        self._manager = None
        self._client = None
        self._server = None
        self._server_thread = None
        self._server_rlock = threading.RLock()
        self._handler = ClientHandler()
        self._service = apsbbsys.server.ClientService(self._handler)

    @_locked('_xport_rlock')
    @_locked('_server_rlock')
    def open(self):
        """Creates UNIX socket and attempts to connect to the path
        specified at initialization time. Raises RuntimeError if already
        open, forwards exceptions raised during connecting.
        """
        if self._sock is not None:
            raise RuntimeError('already open')
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._sock.connect(self._sock_path)
        except:
            self._sock = None
            raise
        self._xport = SocketTransport(self._sock)
        self._xport.crc_16 = ERPC_GENERATED_SHIM_CODE_CRC
        self._arbitrator = erpc.arbitrator.TransportArbitrator(
            self._xport,
            erpc.basic_codec.BasicCodec()
        )
        self._manager = erpc.client.ClientManager(
            self._xport,
            erpc.basic_codec.BasicCodec
        )
        self._manager.arbitrator = self._arbitrator
        self._client = apsbbsys.client.DeviceClient(self._manager)
        self._server = erpc.simple_server.SimpleServer(
            self._arbitrator,
            erpc.basic_codec.BasicCodec
        )
        self._server.add_service(self._service)
        self._server_thread = threading.Thread(
            target=self._client_server,
            name='client-erpc-server'
        )
        self._server_thread.start()

    @_locked('_xport_rlock')
    @_locked('_server_rlock')
    def close(self):
        """Terminates connection."""
        if self._sock is None:
            return
        # attempt to shutdown server gracefully
        self._server.stop()
        self._server_thread.join(2)
        # if graceful attempt failed, close socket (causing exception in server thread)
        if self._server_thread.is_alive():
            self._sock.shutdown(socket.SHUT_RDWR)
        self._server_thread.join()
        # delete object created when opening
        self._server_thread = None
        self._server = None
        self._client = None
        self._manager = None
        self._arbitrator = None
        self._xport = None
        self._sock.close()
        self._sock = None

    def __del__(self):
        self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def _client_server(self):
        _logger.info('started')
        try:
            self._server.run()
        except erpc.transport.ConnectionClosed:
            _logger.info('connection closed')
        except:
            _logger.exception('exception while running erpc server')
        _logger.info('returning')
        return

    def _sync_handler(fn):
        @wraps(fn)
        def _fn(self, *args, **kwargs):
            with self._handler._lock:
                ret = fn(self, *args, **kwargs)
            return ret
        return _fn

    @property
    def button_changed_callback(self):
        """Callback function invoked when button status changes. The
        callback is invoked with a single argument - a boolean flag
        indicating whether button is pressed or not.
        """
        return self._handler._button_changed_callback

    @button_changed_callback.setter
    @_sync_handler
    def button_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._button_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    def vehicle_changed_callback(self):
        """Callback function invoked when vehicle status changes. The
        current PathStatus object is passed to the callback.
        """
        return self._handler._vehicle_changed_callback

    @vehicle_changed_callback.setter
    @_sync_handler
    def vehicle_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._vehicle_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    def barrier_changed_callback(self):
        """Callback function invoked when barrier status changes. The
        current PathStatus object is passed to the callback.
        """
        return self._handler._barrier_changed_callback

    @barrier_changed_callback.setter
    @_sync_handler
    def barrier_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._barrier_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    def intercom_changed_callback(self):
        """Callback function invoked when intercom button status changes.
        Boolean flag representing current input state is passed as the
        single parameter.
        """
        return self._handler._icom_changed_callback

    @intercom_changed_callback.setter
    @_sync_handler
    def intercom_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._icom_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    def breach_changed_callback(self):
        """Callback function invoked when breach input status changes.
        Boolean flag representing current input state is passed as the
        single parameter.
        """
        return self._handler._breach_changed_callback

    @breach_changed_callback.setter
    @_sync_handler
    def breach_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._breach_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    def gpio_changed_callback(self):
        """Callback function invoked when the status of any of the
        general purpose IO configured as input changes. The callback is
        invoked with two arguments - index of the input changed (integer)
        and its current value (bool).
        """
        return self._handler._gpio_changed_callback

    @gpio_changed_callback.setter
    @_sync_handler
    def gpio_changed_callback(self, value):
        if value is None or callable(value):
            self._handler._gpio_changed_callback = value
        else:
            raise TypeError('callback must be callable or None')

    @property
    @_locked('_xport_rlock')
    def firmware_version(self):
        """Queries the firmware version of the backbone hardware and returns
        it as a FirmwareVersion object.
        """
        return self._client.firmware_version

    @property
    @_locked('_xport_rlock')
    def software_reset(self):
        """Performs a software reset of the backbone hardware."""
        return self._client.software_reset

    @property
    @_locked('_xport_rlock')
    def hardware_reset(self):
        """Performs a hardware reset of the backbone."""
        return self._client.hardware_reset

    @property
    @_locked('_xport_rlock')
    def button_is_pressed(self):
        """Queries button status and returns it as a boolean flag."""
        return self._client.btn_is_pressed

    @property
    @_locked('_xport_rlock')
    def button_press_time(self):
        """Returns integer value indicating how long the button has been
        pressed (in milliseconds). Returns 0 if the button is not pressed.
        """
        return self._client.btn_press_time

    @property
    @_locked('_xport_rlock')
    def button_set_invert(self):
        """Sets logic level of the button (active high/low).

        Parameters
        ----------
        enabled : bool
            True for inverted logic (active low), False otherwise.
        """
        return self._client.btn_set_invert

    @property
    @_locked('_xport_rlock')
    def button_get_invert(self):
        """Returns current logic level of the button input as boolean flag."""
        return self._client.btn_get_invert

    @property
    @_locked('_xport_rlock')
    def button_set_enabled(self):
        """Enables or disables button backlight.

        If the backlight is enabled the backbone generates a pulsing waveform
        with the button depressed, the backlight becomes fully lit when
        the button is pressed.

        Parameters
        ----------
        enabled : bool
            True to enable, False to disable.
        """
        return self._client.btn_set_enabled

    @property
    @_locked('_xport_rlock')
    def button_get_enabled(self):
        """Returns boolean flag indicating whether the button backlight is enabled."""
        return self._client.btn_get_enabled

    @property
    @_locked('_xport_rlock')
    def button_set_config(self):
        """Sets button configuration.

        Parameters
        ----------
        enabled : bool
            Enables or disables button backlight.
        invert : bool
            Configures logic level of the button.
        """
        return self._client.btn_set_config

    @_locked('_xport_rlock')
    def button_get_config(self):
        """Returns button configuration as a tuple with 2 boolean flags: enabled and invert."""
        enable = erpc.Reference()
        invert = erpc.Reference()
        self._client.btn_get_config(enable, invert)
        return enable.value, invert.value

    @property
    @_locked('_xport_rlock')
    def rgb_set_colour(self):
        """Configures colour emitted by the RGB module.

        Parameters
        ----------
        colour : Colour
        """
        return self._client.rgb_set_colour

    @_locked('_xport_rlock')
    def rgb_get_colour(self):
        """Returns colour currently emitted by the RGB module."""
        colour = erpc.Reference()
        self._client.rgb_get_colour(colour)
        return colour.value

    @property
    @_locked('_xport_rlock')
    def rgb_set_timings(self):
        """Configures timings of the waveform generated by the RGB module.

        Parameters
        ----------
        timings : Timings
        """
        return self._client.rgb_set_timings

    @_locked('_xport_rlock')
    def rgb_get_timings(self):
        """Returns current timings of the waveform generated by the RGB module."""
        timings = erpc.Reference()
        self._client.rgb_get_timings(timings)
        return timings.value

    @property
    @_locked('_xport_rlock')
    def rgb_set_mode(self):
        """Configures mode of the RGB module.

        Parameters
        ----------
        mode : LightMode
        """
        return self._client.rgb_set_mode

    @property
    @_locked('_xport_rlock')
    def rgb_get_mode(self):
        """Returns current mode of the RGB module."""
        return self._client.rgb_get_mode

    @property
    @_locked('_xport_rlock')
    def rgb_set_coefficients(self):
        """Configures coefficients of the RGB module.

        Parameters
        ----------
        coeffs : Coefficients
        """
        return self._client.rgb_set_coefficients

    @_locked('_xport_rlock')
    def rgb_get_coefficients(self):
        """Returns current coefficients of the waveform generated by the RGB module."""
        coeffs = erpc.Reference()
        self._client.rgb_get_coefficients(coeffs)
        return coeffs.value

    @property
    @_locked('_xport_rlock')
    def rgb_set_config(self):
        """Performs a batch configuration of the RGB module.

        Parameters
        ----------
        mode : LightMode
        timings : Timings
        colour : Colour
        coeffs : Coefficients
        """
        return self._client.rgb_set_config

    @_locked('_xport_rlock')
    def rgb_get_config(self):
        """Queries current configuration of the RGB module and returns it as a tuple
        of 4 elements: LightMode, Timings, Colour and Coefficients.
        """
        mode = erpc.Reference()
        timings = erpc.Reference()
        colour = erpc.Reference()
        coeffs = erpc.Reference()
        self._client.rgb_get_config(mode, timings, colour, coeffs)
        return mode.value, timings.value, colour.value, coeffs.value

    @_locked('_xport_rlock')
    def path_get_status(self):
        """Queries current status of the path, returns a PathStatus object."""
        status = erpc.Reference()
        self._client.path_get_status(status)
        return status.value

    @property
    @_locked('_xport_rlock')
    def path_open(self):
        """Requests opening of the barrier.

        Parameters
        ----------
        force : bool
            Indicates whether operation is forced, i.e. if the barrier
            movement shall be started even if no vehicle is present at
            loop A.
        auto_close : bool
            Indicates whether the barrier shall be closed after a passthrough
            (or retreat) of the vehicle is detected.
        """
        return self._client.path_open

    @property
    @_locked('_xport_rlock')
    def path_close(self):
        """Requests closing of the barrier."""
        return self._client.path_close

    @property
    @_locked('_xport_rlock')
    def path_set_barrier_timeout(self):
        """Configures timeout of the barrier movement.

        Parameters
        ----------
        timeout : int
            Timeout of the barrier operation in milliseconds.
        """
        return self._client.path_set_barrier_timeout

    @property
    @_locked('_xport_rlock')
    def path_get_barrier_timeout(self):
        """Returns current barrier movement timeout value."""
        return self._client.path_get_barrier_timeout

    @property
    @_locked('_xport_rlock')
    def path_set_loops_timeout(self):
        """Configures loops activation timeout, i.e. time after which
        loop timeout flag is raised (when loop is active).

        Parameters
        ----------
        timeout : int
            Value of the timeout in milliseconds.
        """
        return self._client.path_set_loops_timeout

    @property
    @_locked('_xport_rlock')
    def path_get_loops_timeout(self):
        """Returns current value of the loops activation timeout."""
        return self._client.path_get_loops_timeout

    @property
    @_locked('_xport_rlock')
    def path_set_loops_hold(self):
        """Sets loops hold time, i.e. duration after physical input deactivation
        when it is still being reported as active.

        Parameters
        ----------
        timeout : int
            Hold time in milliseconds.
        """
        return self._client.path_set_loops_hold

    @property
    @_locked('_xport_rlock')
    def path_get_loops_hold(self):
        """Returns current loops hold time."""
        return self._client.path_get_loops_hold

    @property
    @_locked('_xport_rlock')
    def path_get_result(self):
        """Returns last tracker result (one of TrackerResult values) or
        0 if no result to be reported.
        """
        return self._client.path_get_result

    @property
    @_locked('_xport_rlock')
    def path_clear_result(self):
        """Clears current tracker result."""
        self._client.path_clear_result

    @property
    @_locked('_xport_rlock')
    def path_set_config(self):
        """Performs batch configuration of the path module.

        Parameters
        ----------
        barrier_timeout : int
            Barrier movement timeout in milliseconds.
        loops_timeout : int
            Loops activation timeout in milliseconds.
        loops_hold : int
            Loops hold time in milliseconds.
        """
        return self._client.path_set_config

    @_locked('_xport_rlock')
    def path_get_config(self):
        """Returns current path module configuration as a tuple consisting
        of 3 integers, corresponding to parameters of the path_set_config method.
        """
        barrier_timeout = erpc.Reference()
        loops_timeout = erpc.Reference()
        loops_hold = erpc.Reference()
        self._client.path_get_config(barrier_timeout, loops_timeout, loops_hold)
        return barrier_timeout.value, loops_timeout.value, loops_hold.value

    @property
    @_locked('_xport_rlock')
    def buzzer_set_frequency(self):
        """Sets frequency of the sound emitted by the buzzer module.

        Parameters
        ----------
        frequency : int
            Frequency of the emitted sound in Hertz.

        NOTE: due to finite resolution of the module the actual frequency may
        slightly differ from the one requested, e.g. when requesting frequency
        of 2kHz the actual frequency (as reported by buzzer_get_frequency method)
        will be 2016Hz.
        """
        return self._client.buzzer_set_frequency

    @property
    @_locked('_xport_rlock')
    def buzzer_get_frequency(self):
        """Returns current frequency of the sound emitted by the buzzer module."""
        return self._client.buzzer_get_frequency

    @property
    @_locked('_xport_rlock')
    def buzzer_enable(self):
        """Starts operation of the buzzer module.

        Parameters
        ----------
        onTime : int
        offTime : int
        repeatCount : int
        """
        return self._client.buzzer_enable

    @property
    @_locked('_xport_rlock')
    def buzzer_enable_ACK(self):
        """Starts operation of the buzzer module with a predefined parameters."""
        return self._client.buzzer_enable_ACK

    @property
    @_locked('_xport_rlock')
    def buzzer_enable_NAK(self):
        """Starts operation of the buzzer module with a predefined parameters."""
        return self._client.buzzer_enable_NAK

    @property
    @_locked('_xport_rlock')
    def intercom_get(self):
        """Returns logical value of the intercom input."""
        return self._client.icom_get

    @property
    @_locked('_xport_rlock')
    def intercom_active_low(self):
        """Logic level of the intercom input."""
        return self._client.icom_get_active_low()

    @intercom_active_low.setter
    @_locked('_xport_rlock')
    def intercom_active_low(self, value):
        self._client.icom_set_active_low(value)

    @property
    @_locked('_xport_rlock')
    def breach_get(self):
        """Returns logical value of the breach input."""
        return self._client.breach_get

    @property
    @_locked('_xport_rlock')
    def breach_active_low(self):
        """Logic level of the breach input."""
        return self._client.breach_get_active_low()

    @breach_active_low.setter
    @_locked('_xport_rlock')
    def breach_active_low(self, value):
        return self._client.breach_set_active_low(value)

    @property
    @_locked('_xport_rlock')
    def gpio_get(self):
        """Returns logic level of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port to query.
        """
        return self._client.gpio_get

    @property
    @_locked('_xport_rlock')
    def gpio_set(self):
        """Sets status of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port to manipulate.
        enable : bool
            Logic state to set.
        """
        return self._client.gpio_set

    @property
    @_locked('_xport_rlock')
    def gpio_set_direction(self):
        """Sets direction of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port to manipulate
        direction : PinDirection
            Direction to set.
        """
        return self._client.gpio_set_direction

    @property
    @_locked('_xport_rlock')
    def gpio_get_direction(self):
        """Queries current direction of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port whose direction to query.
        """
        return self._client.gpio_get_direction

    @property
    @_locked('_xport_rlock')
    def gpio_set_active_low(self):
        """Sets logic level of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port to manipulate
        active_low : bool
            Logic level to apply.
        """
        return self._client.gpio_set_active_low

    @property
    @_locked('_xport_rlock')
    def gpio_get_active_low(self):
        """Gets logic level of the general purpose port.

        Parameters
        ----------
        idx : int
            Index of the port to query.
        """
        return self._client.gpio_get_active_low
