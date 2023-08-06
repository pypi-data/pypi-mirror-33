import threading
import logging
import time
from .common import CODE_MAP, code_by_symbol_id, STX, ETX, ProtocolError
from .serial_device import SerialDevice


class SerialThreadedDevice(object):
    """Threaded Newland device, conforming to serial protocol."""

    def __init__(self, *, port=None, logger=None):
        if logger is None:
            self._logger = logging.getLogger('newland.SerialThreadedDevice')
        else:
            self._logger = logger
        self._dev = SerialDevice(port=port, logger=logger)
        self._dev.close()
        self._callback_lock = threading.Lock()
        self._callback_status = None
        self._callback_data = None
        self._thread_lock = threading.Lock()
        self._thread_cancel = threading.Event()
        self._thread = None
        self._enabled_lock = threading.Lock()
        self._enabled_update = threading.Event()
        self._enabled_codes = []
        self._online = False
        self._data = None
        self._info = None

    def __del__(self):
        self.stop()

    def start(self):
        with self._thread_lock:
            if self._thread is not None:
                if self._thread.is_alive():
                    raise RuntimeError('worker thread is already running')
                self._thread.join()
                self._thread = None
            self._thread = threading.Thread(target=self._worker_fun)
            self._thread.start()

    def stop(self):
        with self._thread_lock:
            if self._thread is not None:
                self._thread_cancel.set()
                self._thread.join()
                self._thread = None
                self._thread_cancel.clear()

    def enable(self, *codes):
        with self._enabled_lock:
            if len(codes) == 0 or codes[0] == 'all':
                for key in CODE_MAP:
                    if key not in self._enabled_codes:
                        self._enabled_codes.append(key)
                        self._enabled_update.set()
            else:
                for code in codes:
                    if code not in CODE_MAP:
                        code = code_by_symbol_id(code)
                    if code not in self._enabled_codes:
                        self._enabled_codes.append(code)
                        self._enabled_update.set()

    def disable(self, *codes):
        with self._enabled_lock:
            if len(codes) == 0 or codes[0] == 'all':
                self._enabled_codes.clear()
                self._enabled_update.set()
            else:
                for code in codes:
                    if code not in CODE_MAP:
                        code = code_by_symbol_id(code)
                    try:
                        self._enabled_codes.remove(code)
                        self._enabled_update.set()
                    except ValueError:
                        pass

    @property
    def enabled_codes(self):
        try:
            codes = self._dev.query_codes_1d()
            codes.update(self._dev.query_codes_2d())
        except:
            return []
        ret = []
        for k, v in codes.items():
            if v:
                ret.append(k)
        return ret

    @property
    def code_scanned_callback(self):
        return self._callback_data

    @code_scanned_callback.setter
    def code_scanned_callback(self, value):
        with self._callback_lock:
            if value is None or callable(value):
                self._callback_data = value
            else:
                raise TypeError('callback object must be either None or a callable')

    @property
    def status_changed_callback(self):
        return self._callback_status

    @status_changed_callback.setter
    def status_changed_callback(self, value):
        with self._callback_lock:
            if value is None or callable(value):
                self._callback_status = value
            else:
                raise TypeError('callback object must be either None or a callable')

    @property
    def is_online(self):
        return self._online

    @property
    def last_data(self):
        return self._data

    @property
    def device_info(self):
        return self._info

    def _invoke_status_callback(self):
        with self._callback_lock:
            if self._callback_status is None:
                self._logger.info('status callback is empty, online=%s', self._online)
            else:
                try:
                    self._callback_status(self, self._online)
                except:
                    self._logger.exception('exception caught from status callback')

    def _invoke_data_callback(self):
        with self._callback_lock:
            if self._callback_data is None:
                self._logger.info('data callback is empty, data=%s', self._data)
            else:
                try:
                    self._callback_data(self, self._data)
                except:
                    self._logger.exception('exception caught from data callback')

    def _read_code(self):
        ret = False
        buf = bytearray()
        while True:
            tmp = self._dev.read()
            if tmp == b'':
                if len(buf) != 0:
                    self._logger.warning('discarding %d bytes of data: %s', len(buf), buf)
                return ret
            buf.extend(tmp)
            while STX in buf and ETX in buf:
                code_data = buf[buf.index(STX)+1:buf.index(ETX)]
                self._data = bytes(code_data[:3]), bytes(code_data[3:])
                buf = buf[buf.index(ETX)+1:]
                self._invoke_data_callback()
                ret = True

    def _configure_device(self):
        # configure RS232 parameters
        try:
            rs232_cfg = self._dev.query_rs232()
            if rs232_cfg['baudrate'] != 115200:
                self._dev.set_rs232_parameters(baudrate=115200)
        except (TimeoutError, ProtocolError):
            self._logger.warning('failed to configure RS232 baudrate')
            return False

        # configure device
        try:
            # disable all codes, light and aiming
            self._dev.set_disable_all()
            self._dev.set_light('off')
            self._dev.set_aiming('off')
            # configure prefixes and suffixes
            self._dev.set_prefix_and_suffix(enable_all=False, prefix_sequence='User-prefix+CodeID+AIM',
                                            user_prefix_enable=True, user_prefix=STX,
                                            user_suffix_enable=True, user_suffix=ETX,
                                            aim_enable=True, code_id_enable=False, terminator_enable=False)
            # configure reading mode, delays, set all codes parameters to defaults
            self._dev.set_reading_mode('auto')
            self._dev.set_delays(enable=True, read_delay=500, same_read_delay=2500)
            for code in CODE_MAP:
                self._dev.set_code_parameters(code, defaults=True, enable=False)
            # store system information
            self._info = self._dev.set_send_system_information()
        except (TimeoutError, ProtocolError):
            self._logger.warning('failed to configure RS232 baudrate')
            return False

        return True

    def _update_enabled_codes(self):
        # check whether enabled codes list changed
        if self._enabled_update.is_set():
            with self._enabled_lock:
                self._dev.set_disable_all()
                for code in self._enabled_codes:
                    self._dev.set_code_parameters(code, enable=True)
                if len(self._enabled_codes) == 0:
                    self._dev.set_light('off')
                    self._dev.set_aiming('off')
                else:
                    self._dev.set_light('on')
                    self._dev.set_aiming('on')
                self._enabled_update.clear()
                return True
        return False

    def _worker_fun(self):
        comm_stamp = 0
        self._logger.info('thread started, opening device')
        try:
            self._dev.open()
        except:
            self._logger.exception('failed to open device')
            return

        # loop until thread is canceled
        while not self._thread_cancel.is_set():

            if not self._online:
                # scan supported baudrates to find device
                try:
                    self._dev.discover_device()
                except TimeoutError:
                    # device not found, wait 1s for cancellation, continue main loop
                    self._thread_cancel.wait(1)
                    continue
                except:
                    self._logger.exception('unexpected error, thread terminating')
                    break

                try:
                    if self._configure_device():
                        # device configured, mark as online, invoke callback
                        self._online = True
                        self._invoke_status_callback()
                        comm_stamp = time.time()
                except:
                    self._logger.exception('unexpected error, thread terminating')
                    break

                with self._enabled_lock:
                    self._enabled_update.set()

            else:
                try:
                    if self._update_enabled_codes():
                        comm_stamp = time.time()
                except (TimeoutError, ProtocolError):
                    self._logger.warning('failed to update enabled codes, device connection lost')
                    self._online = False
                    self._invoke_status_callback()
                    continue
                except:
                    self._logger.exception('unexpected error, thread terminating')
                    break

                # check for any scanned code
                if self._read_code():
                    comm_stamp = time.time()

                if (time.time() - comm_stamp) > 2.5:
                    try:
                        self._dev.ping()
                        comm_stamp = time.time()
                    except TimeoutError:
                        # connection lost
                        self._online = False
                        self._invoke_status_callback()
                    except:
                        self._logger.exception('unexpected error, thread terminating')
                        break

        try:
            self._dev.set_disable_all()
            self._dev.set_light('off')
            self._dev.set_aiming('off')
        except:
            pass
        if self._online:
            self._online = False
            self._invoke_status_callback()
        self._logger.info('thread exiting, closing device')
        self._dev.close()
        return
