import collections

PREFIX1 = b'\x7E\x00'
PREFIX2 = b'\x02\x00'
QUERY = b'\x33'
RESPONSE = b'\x34'
ASK = b'?'
REPLY = b'!'
ACK = b'\x06'
NAK = b'\x15'
STX = b'\x02'
ETX = b'\x03'

CodeMapEntry = collections.namedtuple('CodeMapEntry', ('symbol_id', 'command_prefix', 'code_id'))

CODE_MAP = {
    'Code 128': CodeMapEntry(b'02', '0400', None),
    'GS1-128': CodeMapEntry(b'03', '0412', None),
    'EAN-8': CodeMapEntry(b'04', '0401', None),
    'EAN-13': CodeMapEntry(b'05', '0402', None),
    'UPC-E': CodeMapEntry(b'06', '0403', None),
    'UPC-A': CodeMapEntry(b'07', '0404', None),
    'Interleaved 2 of 5': CodeMapEntry(b'08', '0405', None),
    'ITF-14': CodeMapEntry(b'09', None, None),
    'ITF-6': CodeMapEntry(b'10', None, None),
    'Matrix 2 of 5': CodeMapEntry(b'11', '0406', None),
    'Code 39': CodeMapEntry(b'13', '0408', None),
    'Codabar': CodeMapEntry(b'15', '0409', None),
    'Code 93': CodeMapEntry(b'17', '0410', None),
    'ISBN': CodeMapEntry(b'24', '0416', None),
    'Industrial 25': CodeMapEntry(b'25', '0417', None),
    'Standard 25': CodeMapEntry(b'26', '0418', None),
    'Plessey': CodeMapEntry(b'27', '0419', None),
    'Code 11': CodeMapEntry(b'28', '0415', None),
    'MSI-Plessey': CodeMapEntry(b'29', '0420', None),
    'EAN-UCC Composite': CodeMapEntry(b'30', '0414', None),
    'GS1 Databar': CodeMapEntry(b'31', '0413', None),
    'PDF417': CodeMapEntry(b'32', '0501', '0'),
    'QR Code': CodeMapEntry(b'33', '0502', '1'),
    'Aztec': CodeMapEntry(b'34', '0503', '2'),
    'Data Matrix': CodeMapEntry(b'35', '0504', '3'),
    'Maxicode': CodeMapEntry(b'36', '0508', '4'),
    'Chinese Sensible Code': CodeMapEntry(b'39', '0508', '7')
}

AIM_ID_MAP = {
    b']E': 'EAN/UPC',
    b']C': 'Code 128',
    b']I': 'ITF',
    b']S': 'Industrial 2 of 5',
    b']R': 'Standard 2 of 5',
    b']A': 'Code 39',
    b']F': 'Codabar',
    b']G': 'Code 93',
    b']H': 'Code 11',
    b']e': 'GS1 Databar',
    b']P': 'Plessey',
    b']M': 'MSI-Plessey',
    b']X': 'Matrix 2 of 5',
    b']L': 'PDF417',
    b']d': 'Data Matrix',
    b']Q': 'QR Code'
}


def code_by_symbol_id(symbol_id):
    for key, val in CODE_MAP.items():
        if val.symbol_id == symbol_id:
            return key
    raise KeyError('no code with symbol id {}'.format(symbol_id))


class ProtocolError(UserWarning):
    pass
