import serial
import logging
import threading
import functools
import contextlib
from .common import PREFIX1, PREFIX2, QUERY, RESPONSE, ASK, REPLY, ACK, NAK
from .common import CODE_MAP, code_by_symbol_id, ProtocolError


def _locked(fn):
    @functools.wraps(fn)
    def _fn(self, *args, **kwargs):
        with self._port_rlock:
            ret = fn(self, *args, **kwargs)
        return ret
    return _fn


class SerialDevice(object):
    """Represents device that can be accessed using Serial Command Programming method."""

    def __init__(self, *, port=None, logger=None):
        if logger is None:
            self._logger = logging.getLogger('newland.SerialDevice')
        elif not issubclass(type(logger), logging.Logger):
            raise TypeError('logger must be an instance or a subclass of a Logger')
        else:
            self._logger = logger

        if type(port) not in (str, serial.Serial):
            raise TypeError('port is expected to be either a path to device or a Serial object')
        self._port_rlock = threading.RLock()
        if type(port) is serial.Serial:
            self._logger.debug('using user-supplied Serial object')
            self._port = port
            self._port.apply_settings({'timeout': 1, 'exclusive': True})
        else:
            self._logger.debug('creating new Serial object, path=%s', port)
            self._port = serial.Serial(port, timeout=1, exclusive=True)

    @_locked
    def open(self):
        if not self._port.is_open:
            self._port.open()

    @_locked
    def close(self):
        self._port.close()

    @_locked
    def read(self, count=-1):
        if count == 0:
            return b''
        buf = bytearray()
        while True:
            dlen = 1 if count < 0 else count - len(buf)
            tmp = self._port.read(dlen)
            if tmp == b'':
                if count < 0 or len(buf) > 0:
                    break
                continue
            buf.extend(tmp)
            if 0 < count == len(buf):
                break
        return bytes(buf)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @_locked
    def ping(self):
        self._port.write(ASK)
        while True:
            rsp = self._port.read(1)
            if rsp == b'':
                raise TimeoutError()
            elif rsp == REPLY:
                return

    @_locked
    def query(self, *data):
        frame = bytearray(PREFIX1)
        dd = bytearray()
        for d in data:
            if type(d) is int:
                dd.extend(d.to_bytes(1, 'big'))
            else:
                dd.extend(d)
        ll = (len(dd) + 1).to_bytes(2, 'big')
        frame.extend(ll)
        frame.extend(QUERY)
        frame.extend(dd)
        lrc = 0xFF
        for d in frame[2:]:
            lrc ^= d
        frame.append(lrc)
        self._port.write(frame)
        tmp = self._port.read(2)
        if tmp != PREFIX2:
            raise ProtocolError('expecting {}, got {}'.format(PREFIX2, tmp))
        lrc = 0xFF
        ll = self._port.read(2)
        for l in ll:
            lrc ^= l
        ll = int.from_bytes(ll, 'big')
        t = self._port.read(1)
        if t != RESPONSE:
            raise ProtocolError('expecting {}, got {}'.format(RESPONSE, t))
        lrc ^= t[0]
        data = self._port.read(ll - 1)
        if len(data) != ll - 1:
            raise ProtocolError('expecting {} bytes of data, got {}'.format(ll - 1, len(data)))
        for d in data:
            lrc ^= d
        check_val = self._port.read(1)
        if len(check_val) != 1:
            raise ProtocolError('expecting check value, got nothing')
        if lrc != check_val[0]:
            raise ProtocolError('invalid check value, expecting {}, got {}'.format(lrc, check_val[0]))
        return data

    @_locked
    def set(self, command, data=None):
        frame = bytearray(b'nls')
        if type(command) is str:
            command = command.encode('ascii')
        frame.extend(command)
        if data is not None:
            frame.extend(b'=')
            if type(data) is int:
                frame.extend(str(data).encode('ascii'))
            elif type(data) is str:
                frame.extend(('"{}"'.format(data)).encode('ascii'))
            elif type(data) in (bytes, bytearray):
                frame.extend(b'0x')
                frame.extend(data.hex().encode('ascii'))
            else:
                raise TypeError('data may be an integer, string or a bytes-like object')
        frame.extend(b';')
        self._port.write(frame)
        rsp = bytearray()
        while True:
            tmp = self._port.read(1)
            if tmp == b'':
                raise ProtocolError('expecting response, but none read')
            elif tmp == ACK:
                break
            elif tmp == NAK:
                raise ProtocolError('command not acknowledged: {}'.format(frame))
            rsp.extend(tmp)
        if len(rsp) == 0:
            return None
        return rsp

    def query_rs232(self):
        data = int.from_bytes(self.query(b'\x30'), 'big')
        ret = dict()
        ret['baudrate'] = ([1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200])[data & 0x0F]
        ret['parity'] = (['none', 'even', 'odd'])[(data >> 4) & 0x03]
        ret['stop bits'] = ((data >> 6) & 0x01) + 1
        ret['data bits'] = ([5, 6, 7, 8])[(data >> 7) & 0x03]
        return ret

    def query_codes_1d(self):
        data = self.query(b'\x32')
        ret = dict()
        ret['ZASETUP'] = (data[0] & 0x01) != 0
        ret['SETUP 128'] = (data[0] & 0x02) != 0
        ret['Code 128'] = (data[0] & 0x04) != 0
        ret['GS1-128'] = (data[0] & 0x08) != 0
        ret['EAN-8'] = (data[0] & 0x10) != 0
        ret['EAN-13'] = (data[0] & 0x20) != 0
        ret['UPC-E'] = (data[0] & 0x40) != 0
        ret['UPC-A'] = (data[0] & 0x80) != 0
        ret['Interleaved 2 of 5'] = (data[1] & 0x01) != 0
        ret['ITF-14'] = (data[1] & 0x02) != 0
        ret['ITF-6'] = (data[1] & 0x04) != 0
        ret['Matrix 2 of 5'] = (data[1] & 0x08) != 0
        ret['Code 39'] = (data[1] & 0x20) != 0
        ret['Codabar'] = (data[1] & 0x80) != 0
        ret['Code 93'] = (data[2] & 0x02) != 0
        ret['ISBN'] = (data[3] & 0x01) != 0
        ret['Industrial 25'] = (data[3] & 0x02) != 0
        ret['Standard 25'] = (data[3] & 0x04) != 0
        ret['Plessey'] = (data[3] & 0x08) != 0
        ret['Code 11'] = (data[3] & 0x10) != 0
        ret['MSI-Plessey'] = (data[3] & 0x20) != 0
        ret['EAN-UCC Composite'] = (data[3] & 0x40) != 0
        ret['GS1 Databar'] = (data[3] & 0x80) != 0
        return ret

    def query_codes_2d(self):
        data = self.query(b'\x33')
        ret = {'PDF417': (data[0] & 0x01) != 0,
               'QR Code': (data[0] & 0x02) != 0,
               'Aztec': (data[0] & 0x04) != 0,
               'Data Matrix': (data[0] & 0x08) != 0,
               'Maxicode': (data[0] & 0x10) != 0,
               'Chinese Sensible Code': (data[0] & 0x80) != 0}
        return ret

    def query_codes_parameter(self, *codes):
        ret = {}
        if len(codes) == 0 or (len(codes) == 1 and codes[0] == 'all'):
            for key, val in CODE_MAP.items():
                self._logger.debug('querying parameters of %s (%s)', key, val.symbol_id)
                try:
                    data = self.query(b''.join([b'\x43', val.symbol_id]))
                    if not data.startswith(val.symbol_id):
                        raise ProtocolError('expecting symbol id {}, got {}'.format(val.symbol_id, data[:2]))
                    ret[key] = data[2:]
                except ProtocolError:
                    ret[key] = None
            return ret
        for code in codes:
            if type(code) is str:
                name = code
                symbol_id = CODE_MAP[code].symbol_id
            elif type(code) in (bytes, bytearray):
                if code == b'00':
                    name = 'ZASETUP'
                else:
                    name = code_by_symbol_id(code)
                symbol_id = code
            else:
                raise TypeError('code must be either a string or a symbol id')

            try:
                data = self.query(b''.join([b'\x43', symbol_id]))
                if not data.startswith(symbol_id):
                    raise ProtocolError('expecting symbol id {}, got {}'.format(symbol_id, data[:2]))
                ret[name] = data[2:]
            except ProtocolError:
                ret[name] = None
        return ret

    def query_twin_barcode(self):
        ret = self.query(b'\x4801')
        if not ret.startswith(b'01'):
            raise ProtocolError('expecting {}, got {}'.format(b'01', ret[:2]))
        if ret[2] == 0x30:
            return 'single-only'
        elif ret[2] == 0x32:
            return 'twin-only'
        elif ret[2] == 0x31:
            return 'both'
        raise ProtocolError('expecting 0x30-0x32, got 0x{:X}'.format(ret[2]))

    def query_send_product_info(self):
        ret = self.query(b'\x4800')
        if not ret.startswith(b'00'):
            raise ProtocolError('expecting {}, got {}'.format(b'00', ret[:2]))
        if ret[2] == 0x30:
            return False
        elif ret[2] == 0x31:
            return True
        raise ProtocolError('expecting 0x30 or 0x31, got 0x{:X}'.format(ret[2]))

    def query_decode_mirror_images(self):
        ret = self.query(b'\x4E')
        if ret[0] == 0x30:
            return False
        elif ret[0] == 0x33:
            return True
        raise ProtocolError('expecting 0x30 or 0x33, got 0x{:X}'.format(ret[0]))

    def query_beep(self):
        rsp = self.query(b'\x4F')
        ret = dict()
        ret['decoding'] = (rsp[0] & 0x01) != 0
        ret['power on'] = (rsp[0] & 0x02) != 0
        ret['type'] = int(rsp[1:2])
        ret['loudness'] = 'high' if rsp[2] == 0x30 else ('medium' if rsp[2] == 0x31 else 'low')
        return ret

    def query_message_pack(self):
        rsp = self.query(b'\x4600')
        if not rsp.startswith(b'000'):
            raise ProtocolError('expecting {}, got {}'.format(b'000', rsp[:3]))
        if rsp[3] == 0x30:
            return False
        elif rsp[3] == 0x31:
            return True
        raise ProtocolError('expecting 0x30 or 0x31, got 0x{:X}'.format(rsp[3]))

    def query_imaging_exposure(self):
        rsp = self.query(b'\x44060')
        if not rsp.startswith(b'06'):
            raise ProtocolError('expecting {}, got {}'.format(b'06', rsp[:2]))
        if rsp[3] == 0x30:
            return 'normal mode'
        elif rsp[3] == 0x31:
            return 'reflections eliminating mode'
        raise ProtocolError('expecting 0x30 or 0x31, got 0x{:X}'.format(rsp[3]))

    def query_message_interception(self):
        data = self.query(b'\x50')
        if len(data) != 61:
            raise ProtocolError('expecting 61 bytes of data, got {}'.format(len(data)))
        if data[0] == 0x30:
            return None
        elif data[0] != 0x31:
            raise ProtocolError('expecting 0x30 or 0x31, got 0x{:X}'.format(data[0]))
        ret = []
        for i in range(3):
            dd = data[1+20*i:1+20*(i+1)]
            symbol_id = dd[0]
            ret.append({
                'Symbol ID': symbol_id,
                'data': dd[1::]
            })
        return ret

    def query_light_and_aiming(self):
        data = int.from_bytes(self.query(0x35), 'big')
        aiming = data & 0x03
        light = (data >> 2) & 0x03
        ret = dict()
        if aiming == 0:
            ret['aiming'] = 'normal'
        elif aiming == 1:
            ret['aiming'] = 'on'
        elif aiming == 2:
            ret['aiming'] = 'off'
        else:
            raise ProtocolError('unexpected aiming value')
        if light == 0:
            ret['light'] = 'normal'
        elif light == 1:
            ret['light'] = 'on'
        elif light == 2:
            ret['light'] = 'off'
        else:
            raise ProtocolError('unexpected light value')
        return ret

    def query_prefix_and_suffix(self):
        data = self.query(0x37)
        prefix_data = data[0:2+data[1]]
        suffix_data = data[2+data[1]:]
        ret = dict(
            prefix=dict(
                enabled=(prefix_data[0] in [0x01, 0x31]),
                value=prefix_data[2:]
            ),
            suffix=dict(
                enabled=(suffix_data[0] in [0x01, 0x31]),
                value=suffix_data[2:]
            )
        )
        return ret

    def query_aim_mode(self):
        return int(self.query(0x39))

    def query_terminal_characters(self):
        data = self.query(0x40)
        return (data[0] == 0x31), data[2:2+data[1]]

    def query_min_max_code_length(self, *codes):
        ret = dict()
        if codes is None or len(codes) == 0 or (len(codes) == 1 and codes[0] == 'all'):
            codes = CODE_MAP.keys()
        for code in codes:
            if code not in CODE_MAP:
                code = code_by_symbol_id(code)
            data = self.query(0x41, CODE_MAP[code].symbol_id)
            if not data.startswith(CODE_MAP[code].symbol_id):
                raise ProtocolError('expecting matching symbol ID ({}), got {}'.format(CODE_MAP[code].symbol_id,
                                                                                       data[:2]))
            ret[code] = int(data[6:10], 16), int(data[4:6], 16)
        return ret

    def query_prefix_order(self):
        data = self.query(0x42)
        if data[0] == 0x30:
            return 'CodeID+AIM+User-prefix'
        elif data[0] == 0x31:
            return 'CodeID+User-prefix+AIM'
        elif data[0] == 0x32:
            return 'AIM+CodeID+User-prefix'
        elif data[0] == 0x33:
            return 'AIM+User-prefix+Code ID'
        elif data[0] == 0x34:
            return 'User-prefix+CodeID+AIM'
        elif data[0] == 0x35:
            return 'User-prefix+AIM+Code ID'
        raise ProtocolError('expecting value in range(0x30, 0x36), got 0x(:X}'.format(data[0]))

    def query_reading_mode(self):
        data = self.query(0x44, b'000')
        if not data.startswith(b'00'):
            raise ProtocolError('expecting {}, got {}'.format(b'00', data[:2]))
        if data[2] == 0x30:
            return 'trigger'
        elif data[2] == 0x31:
            return 'auto'
        elif data[2] == 0x32:
            return 'continuous'
        raise ProtocolError('expecting value in range(0x30, 0x33), got 0x{:X}'.format(data[2]))

    def query_sensitivity(self):
        data = self.query(0x44, b'020')
        if not data.startswith(b'021'):
            raise ProtocolError('expecting leading b\'021\', got {}'.format(data[:3]))
        return int(data[3:])

    def query_reading_delay(self):
        data = self.query(0x44, b'030')
        if not data.startswith(b'0300'):
            raise ProtocolError('expecting leading b\'0300\', got {}'.format(data[:4]))
        return int(data[4:])

    def query_duplicate_reading_delay(self):
        data = self.query(0x44, b'031')
        if not data.startswith(b'031'):
            raise ProtocolError('expecting leading b\'031\', got {}'.format(data[:3]))
        return (data[3] == 0x31), int(data[4:])

    def query_version(self):
        data = self.query(0x47)
        return data.decode('ascii')

    def query_esn(self):
        data = self.query(0x48, b'020')
        if not data.startswith(b'02'):
            raise ProtocolError('expecting leading b\'02\', got {}'.format(data[:2]))
        return data[4:4+int(data[2:4])]

    def query_serial_number(self):
        data = self.query(0x48, b'030')
        if not data.startswith(b'03'):
            raise ProtocolError('expecting leading b\'03\', got {}'.format(data[:2]))
        return data[4:4+int(data[2:4])]

    def query_manufacture_date(self):
        data = self.query(0x48, b'040')
        if not data.startswith(b'04'):
            raise ProtocolError('expecting leading b\'04\', got {}'.format(data[:2]))
        return data[4:4+int(data[2:4])]

    def set_programming_mode_enter(self):
        self.set('0006010')

    def set_programming_mode_exit(self):
        self.set('0006000')

    @_locked
    @contextlib.contextmanager
    def programming_mode(self):
        self.set_programming_mode_enter()
        yield
        self.set_programming_mode_exit()

    def set_factory_defaults(self):
        self.set('0001000')

    def set_disable_all(self):
        self.set('0001010')

    def set_enable_all(self):
        self.set('0001020')

    def set_disable_all_1d(self):
        self.set('0001030')

    def set_enable_all_1d(self):
        self.set('0001040')

    def set_disable_all_2d(self):
        self.set('0001050')

    def set_enable_all_2d(self):
        self.set('0001060')

    def set_store_user_defaults(self):
        self.set('0001150')

    def set_load_user_defaults(self):
        self.set('0001160')

    def set_twin_barcode_1d(self, mode='both'):
        if mode == 'single-only':
            cmd = '0001070'
        elif mode == 'both':
            cmd = '0001080'
        elif mode == 'twin-only':
            cmd = '0001090'
        else:
            raise ValueError('mode may be one of (\'single-only\', \'both\', \'twin-only\')')
        self.set(cmd)

    def set_send_system_information(self):
        rsp = self.set('0003000')
        return rsp.decode('ascii')

    def set_send_system_information_at_power_on(self, enable=True):
        if enable:
            self.set('0007010')
        else:
            self.set('0007000')

    def set_communication_interface(self, interface):
        if interface == 'rs232':
            cmd = '1100000'
        elif interface == 'usb-datapipe':
            cmd = '1100010'
        elif interface == 'usb-kbw':
            cmd = '1100020'
        elif interface == 'usb-com':
            cmd = '1100060'
        elif type(interface) is not str:
            raise TypeError('interface must be a string')
        else:
            raise ValueError('interface must be one of \'rs232\', \'usb-datapipe\', \'usb-kbw\' or \'usb-com\'')
        self.set(cmd)

    @_locked
    def set_rs232_parameters(self, *, baudrate=None, parity=None, stop_bits=None, data_bits=None):
        baudrate_map = {1200: '0',
                        2400: '1',
                        4800: '2',
                        9600: '3',
                        14400: '4',
                        19200: '5',
                        38400: '6',
                        57600: '7',
                        115200: '8'}
        parity_map = {'none': '0', 'even': '1', 'odd': '2'}
        stop_bits_map = {1: '0', 2: '1'}
        data_bits_map = {5: '0', 6: '1', 7: '2', 8: '3'}
        cmd = bytearray()
        settings = dict()
        if baudrate is not None:
            if baudrate not in baudrate_map:
                raise ValueError('baudrate not supported, must be one of {}'.format(baudrate_map.keys()))
            cmd.extend(('nls01000{}0;'.format(baudrate_map[baudrate])).encode('ascii'))
            settings['baudrate'] = baudrate
        if parity is not None:
            if parity not in parity_map:
                raise ValueError('parity not supported, must be one of {}'.format(parity_map.keys()))
            cmd.extend(('nls01010{}0;'.format(parity_map[parity])).encode('ascii'))
            if parity == 'none':
                settings['parity'] = 'N'
            elif parity == 'odd':
                settings['parity'] = 'O'
            else:
                settings['parity'] = 'E'
        if stop_bits is not None:
            if stop_bits not in stop_bits_map:
                raise ValueError('stop_bits not supported, must be one of {}'.format(stop_bits_map.keys()))
            cmd.extend(('nls01020{}0;'.format(stop_bits_map[stop_bits])).encode('ascii'))
            settings['stopbits'] = stop_bits
        if data_bits is not None:
            if data_bits not in data_bits_map:
                raise ValueError('data_bits not supported, must be one of {}'.format(data_bits_map.keys()))
            cmd.extend(('nls01030{}0;'.format(data_bits_map[data_bits])).encode('ascii'))
            settings['bytesize'] = data_bits
        if len(cmd) > 0:
            self._port.write(cmd)
            self._port.flush()
            self._port.read()
            self._port.apply_settings(settings)
            self._port.flushInput()
            self.ping()

    def set_light(self, mode):
        mode_lst = ['flash', 'on', 'off', 'on-scan']
        msg = 'mode not supported, must be one of {} or an integer in range(0, 4)'.format(mode_lst)
        if type(mode) is str:
            try:
                cmd = '02000{}0'.format(mode_lst.index(mode))
            except ValueError:
                raise ValueError(msg)
        elif type(mode) is int:
            if mode not in range(4):
                raise ValueError(msg)
            cmd = '02000{}0'.format(mode)
        else:
            raise TypeError(msg)
        self.set(cmd)

    def set_aiming(self, mode):
        aiming_lst = ['flash', 'on', 'off', 'sense']
        msg = 'mode not supported, must be one of {} or an integer in range(0, {})'.format(aiming_lst, len(aiming_lst))
        if type(mode) is str:
            try:
                cmd = '02010{}0'.format(aiming_lst.index(mode))
            except ValueError:
                raise ValueError(msg)
        elif type(mode) is int:
            if mode not in range(len(aiming_lst)):
                raise ValueError(msg)
            cmd = '02010{}0'.format(mode)
        else:
            raise TypeError(msg)
        self.set(cmd)

    def set_good_read_beep(self, enable):
        if enable:
            cmd = '0203010'
        else:
            cmd = '0203000'
        self.set(cmd)

    def set_decode_mirror_images(self, enable):
        if enable:
            cmd = '0202030'
        else:
            cmd = '0202000'
        self.set(cmd)

    def set_prefix_and_suffix(self, *, enable_all=None, prefix_sequence=None,
                              user_prefix_enable=None, user_prefix=None,
                              user_suffix_enable=None, user_suffix=None,
                              aim_enable=None, code_id_enable=None,
                              terminator_enable=None, terminator_characters=None):
        prefix_sequence_lst = ['CodeID+AIM+User-prefix', 'CodeID+User-prefix+AIM',
                               'AIM+CodeID+User-prefix', 'AIM+User-prefix+CodeID',
                               'User-prefix+CodeID+AIM', 'User-prefix+AIM+CodeID']
        if enable_all is not None:
            if bool(enable_all):
                self.set('0311010')
            else:
                self.set('0311000')
        if prefix_sequence is not None:
            msg = 'prefix sequence not supported, must be one of {} or an integer in range(0, {})'.format(
                prefix_sequence_lst,
                len(prefix_sequence_lst)
            )
            if type(prefix_sequence) is str:
                try:
                    cmd = '03170{}0'.format(prefix_sequence_lst.index(prefix_sequence))
                    self.set(cmd)
                except ValueError:
                    raise ValueError(msg)
            elif type(prefix_sequence) is int:
                if prefix_sequence not in range(len(prefix_sequence_lst)):
                    raise ValueError(msg)
                cmd = '03170{}0'.format(prefix_sequence)
            else:
                raise TypeError(msg)
            self.set(cmd)
        if user_prefix_enable is not None:
            if bool(user_prefix_enable):
                self.set('0305010')
            else:
                self.set('0305000')
        if user_prefix is not None:
            self.set('0300000', user_prefix)
        if user_suffix_enable is not None:
            if bool(user_suffix_enable):
                self.set('0306010')
            else:
                self.set('0306000')
        if user_suffix is not None:
            self.set('0301000', user_suffix)
        if aim_enable is not None:
            if type(aim_enable) is int:
                if aim_enable not in range(4):
                    raise ValueError('aim enable must be either a bool or an integer in range(0, 4)')
                cmd = '03080{}0'.format(aim_enable)
            elif bool(aim_enable):
                cmd = '0308030'
            else:
                cmd = '0308000'
            self.set(cmd)
        if code_id_enable is not None:
            if bool(code_id_enable):
                self.set('0307010')
            else:
                self.set('0307000')
        if terminator_enable is not None:
            if bool(terminator_enable):
                self.set('0309010')
            else:
                self.set('0309000')
        if terminator_characters is not None:
            self.set('0310000', terminator_characters)

    def set_code_id(self, *config, defaults=None):
        if defaults is not None and bool(defaults):
            self.set('0307020')
        for code, code_id in config:
            if code not in CODE_MAP:
                code = code_by_symbol_id(code)
            if CODE_MAP[code].code_id is None:
                cmd = '0004{}0'.format(CODE_MAP[code].symbol_id.decode('ascii'))
            else:
                cmd = '00050{}0'.format(CODE_MAP[code].code_id)
            self.set(cmd, code_id)

    def set_reading_mode(self, mode):
        mode_lst = ['trigger', 'auto', 'continuous']
        msg = 'reading mode must be either one of {} or an integer in range(0, {})'.format(mode_lst, len(mode_lst))
        if type(mode) is str:
            try:
                cmd = '03020{}0'.format(mode_lst.index(mode))
            except ValueError:
                raise ValueError(msg)
        elif type(mode) is int:
            if mode not in range(len(mode_lst)):
                raise ValueError(msg)
            cmd = '03020{}0'.format(mode)
        else:
            raise TypeError(msg)
        self.set(cmd)

    def set_sensitivity(self, value):
        value_lst = ['low', 'normal', 'high', 'higher']
        msg = 'sensitivity must be either one of {} or an integer in range(0, 51)'
        if type(value) is str:
            try:
                cmd = '03120{}0'.format(value_lst.index(value))
                self.set(cmd)
            except ValueError:
                raise ValueError(msg)
        elif type(value) is int:
            if value not in range(51):
                raise ValueError(msg)
            self.set('0312040', value)
        else:
            raise TypeError(msg)

    def set_delays(self, *, enable=None, read_delay=None, same_read_delay=None):
        if enable is not None:
            if bool(enable):
                self.set('0313030')
            else:
                self.set('0313020')
        if read_delay is not None:
            if type(read_delay) is not int:
                raise TypeError('delays must be integers')
            self.set('0313000', read_delay)
        if same_read_delay is not None:
            if type(same_read_delay) is not int:
                raise TypeError('delays must be integers')
            self.set('0313010', same_read_delay)

    def set_code_parameters(self, code, *, defaults=False, enable=None, min_length=None, max_length=None):
        if code not in CODE_MAP:
            code = code_by_symbol_id(code)
        if CODE_MAP[code].command_prefix is None:
            self._logger.warning('unable to set parameters for %s, no command prefix', code)
            return
        if bool(defaults):
            cmd = '{}000'.format(CODE_MAP[code].command_prefix)
            self.set(cmd)
        if enable is not None:
            cmd = '{}0{}0'.format(CODE_MAP[code].command_prefix, '2' if bool(enable) else '1')
            self.set(cmd)
        if min_length is not None:
            if type(min_length) is not int:
                raise TypeError('lengths must be integers')
            cmd = '{}030'.format(CODE_MAP[code].command_prefix)
            self.set(cmd, min_length)
        if max_length is not None:
            if type(max_length) is not int:
                raise TypeError('lengths must be integers')
            cmd = '{}040'.format(CODE_MAP[code].command_prefix)
            self.set(cmd, max_length)

    @_locked
    def discover_device(self):
        try:
            self.ping()
            return
        except TimeoutError:
            pass
        for baudrate in [1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200]:
            self._logger.debug('setting baudrate to %dbps', baudrate)
            self._port.flush()
            self._port.apply_settings({'baudrate': baudrate})
            self._port.flushInput()
            try:
                self.ping()
                return
            except TimeoutError:
                pass
        raise TimeoutError()
