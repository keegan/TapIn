#!/usr/bin/env python3
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from typing import List
import traceback
import requests
import base64
import time
from settings import *

MIFARE_CLASSIC_1K_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"

SUCCESS_STATUS = (0x90, 0x00)
FAIL_STATUS = (0x63, 0x00)


class TapObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            card.connection = card.createConnection()
            card.connection.connect()
            try:
                self.callback(card.connection)
            except Exception as e:
                traceback.print_exc()
        for card in removedcards:
            print("Card disconnected")


class NFCError(RuntimeError):
    pass


def read_sector(connection, sector_num: int, key: List[int], full_sector: bool = False):
    """Return the data stored in the specified sector.  """
    data = []
    auth_block = sector_num * 4
    # Authenticate to the sector
    load_key(connection, key)  # load keys
    authenticate(connection, auth_block)  # act upon keys
    # Read the blocks, omitting the key block if the full sector is not requested
    for block_number in range(sector_num * 4, (sector_num + 1) * 4 - (0 if full_sector else 1)):
        block_data = read_data(connection, block_number)
        data.append(block_data)
    return sum(data, [])
    # return hex_mat_to_string(data)


def string_to_hex_mat(data):
    """ Return n-length array of length-16 arrays of integers

        The length-16 arrays are right zero-padded.
    """
    blocks = [data[i:i + 16] for i in range(0, len(data), 16)]

    blocks[-1] += '\x00' * (16 - len(blocks[-1]))  # zero-pad

    return [[int("{0:2x}".format(ord(c)), 16) for c in block] for block in blocks]


def hex_mat_to_string(data):
    """ Return string from hex matrix. Inverse of string_to_hex_mat"""
    return ''.join([''.join([chr(h) for h in block]) for block in data]).strip('\x00')


def write_string(connection, data):
    block_data = string_to_hex_mat(data)
    auth_block = None
    for index, data in enumerate(block_data):
        block = BLOCKS[index]
        block_number = block[0]
        if auth_block != block[1]:
            auth_block = block[1]
            load_key(connection, key_from_string(KEYS[auth_block // 4]))
            authenticate(connection, block_number)
        write_data(connection, block_number, data)


def check_status(sw1, sw2):
    """ Returns length-2 tuple with status of command

    status[0] is boolean indicating whether command was successful
    status[1] is a status message

    :sw1: first byte of response trailer
    :sw2: second byte of response trailer

    """
    status = (sw1, sw2)
    if status == SUCCESS_STATUS:
        return (True, "The operation completed successfully.")
    if status == FAIL_STATUS:
        return (False, "The operation failed.")
    if status == (0x6A, 0x81):
        return (False, "The function is not supported.")


def key_from_string(key):
    """ Returns hex array from a string
    """
    return [int(key[i:i + 2], 16) for i in range(0, len(key), 2)]


def get_data(connection, ats=False):
    """ Returns the serial number by default

        If ats=True, returns the ATS
    """

    apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    if ats:
        apdu[2] = 0x01
        apdu[4] = 0x04

    # data, sw1, sw2 = connection.transmit(apdu)
    data, sw1, sw2 = connection.transmit(apdu)

    if (sw1, sw2) == SUCCESS_STATUS:
        return data
    raise NFCError("Failed to retrieve data from card.", "get_data", (sw1, sw2))
    # status = check_status(sw1, sw2)
    # if status[0]:
    #    return True, data
    # else:
    #    return False, status[1]


def load_key(connection, key, key_number=0x00):
    """ Loads key into reader

        key is length-6 array of hexadecimals
    """
    apdu = [0xFF, 0x82, 0x00, key_number, 0x06]
    apdu += key

    data, sw1, sw2 = connection.transmit(apdu)

    if (sw1, sw2) == SUCCESS_STATUS:
        return data
    raise NFCError("Failed to load key into card.", "load_key", (sw1, sw2))
    # status = check_status(sw1, sw2)
    # if status[0]:
    #    return True, data
    # else:
    #    return False, status[1]


def authenticate(connection, block_number, key_type=0x60, key_number=0x00):
    """ Authenticate with a memory block
        Must specify the data BLOCK. However, after auth for that block,
        other blocks from the same sector are accessible.
    """
    apdu = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block_number, key_type, key_number]
    data, sw1, sw2 = connection.transmit(apdu)

    if (sw1, sw2) == SUCCESS_STATUS:
        return data
    raise NFCError("Failed to authenticate to card.", "authenticate", (sw1, sw2))
    # status = check_status(sw1, sw2)
    # if status[0]:
    #    return True, data
    # else:
    #    return False, status[1]


def read_data(connection, block_number, num_bytes=0x10):
    """ Read binary data from a block
    """
    apdu = [0xFF, 0xB0, 0x00, block_number, num_bytes]
    data, sw1, sw2 = connection.transmit(apdu)

    if (sw1, sw2) == SUCCESS_STATUS:
        return data
    raise NFCError("Failed to read data from block.", "read_data", (sw1, sw2))
    # status = check_status(sw1, sw2)
    # if status[0]:
    #    return True, data
    # else:
    #    return False, status[1]


def write_data(connection, block_number, data, num_bytes=0x10, auth=False):
    """ Write data to block
    """
    if block_number == 0x00:
        print("Cannot write to 0x00")
        return
    if (block_number + 1) % 4 == 0 and not auth:
        print("Refusing to write data to auth block. Use auth=True to override.")

    apdu = [0xFF, 0xD6, 0x00, block_number, num_bytes]
    apdu += data
    data, sw1, sw2 = connection.transmit(apdu)

    if (sw1, sw2) == SUCCESS_STATUS:
        return data
    raise NFCError("Failed to read write data to block.", "write_data", (sw1, sw2))
    # status = check_status(sw1, sw2)
    # if status[0]:
    #    return True, data
    # else:
    #    return False, status[1]


def handle_connection(connection):
    atr = toHexString(connection.getATR())
    if not atr == MIFARE_CLASSIC_1K_ATR:
        print("Card is incompatible.")
        return False
    print("Card connected")
    # try:
    #    print(f'STR: {read_string(connection)}')
    # except NFCError as e:
    #    print(f'read_string error: {e}')
    # print("hi")
    for i in range(1, 16):
        print("loopenter")
        key = [0xFF] * 6
        try:
            print(f'SCT {i}: {read_sector(connection, i, key)}')
        except NFCError as e:
            print(f"Error reading block {i}: {e}")


def poll():
    """poll for card
    """
    cardmonitor = CardMonitor()
    cardobserver = TapObserver()
    cardmonitor.addObserver(cardobserver)

    def delete():
        print('Stopping')
        cardmonitor.deleteObserver(cardobserver)

    return delete


def handle_card(connection):
    if toHexString(connection.getATR()) != MIFARE_CLASSIC_1K_ATR:
        requests.post(API_LOC,
                      data={'token': TAPD_TOKEN, 'hostname': TAPD_HOSTNAME, 'success': False, 'error_code': 'unknown',
                            'extra': {}})
        print("Errored!")
        return
    # Read UUID sector.
    try:
        sector = read_sector(connection, 1, [0xFF] * 6)
    except NFCError:
        requests.post(API_LOC,
                      data={'token': TAPD_TOKEN, 'hostname': TAPD_HOSTNAME, 'success': False, 'error_code': 'unknown',
                            'extra': {}})
        print("Errored!")
        return
    # convert the sectors to ascii, and then concatenate to a UUID string.
    # The string representaion of a UUID is 36 bytes.
    as_str = "".join([chr(x) for x in sector])
    uuid = as_str[:36]
    # Start a session with the server, so we can get CSRF tokens
    session = requests.Session()
    # Get card information from server, also setting CSRF token in the process
    response = session.get(API_LOC + f"?token={TAPD_TOKEN}&hostname={TAPD_HOSTNAME}&uid={uuid}")
    sectors = response.json()['segments']
    print(response.cookies)
    #csrftoken = response.cookies['csrftoken']
    csrftoken = "me_too_thanks"
    # verify sectors one at a time
    for i, sector in enumerate(sectors):
        # The backend returns URL SAFE base64, so decode it into bytes and then make it an array
        # THE BACKEND DOES NOT RETURN NORMAL BASE64.  REPEAT.  THE BASE64 RETURNED IS NOT NORMAL.
        # The returned base64 MUST be decoded with base64.urlsafe_b64decode()
        # it ALSO requires additional padding, up to some arbitrairy nubmer of characters.
        # good luck.
        key = sector['key']
        fragment = sector['contents']
        key += '=' * (-len(key) % 4)  # restore padding
        fragment += '=' * (-len(fragment) % 4)  # restore padding
        key = list(base64.urlsafe_b64decode(key.encode("UTF-8")))
        fragment = list(base64.urlsafe_b64decode(fragment.encode("UTF-8")))
        try:
            contents = read_sector(connection, i + 2, key)
        except NFCError as e:
            requests.post(API_LOC,
                          data={'token': TAPD_TOKEN, 'hostname': TAPD_HOSTNAME, 'success': False, 'error_code': 'auth',
                                'extra': {'failed_sector': i}, 'csrfmiddlewaretoken': csrftoken})
            # logic for sending error
            print("Errored! @ read error")
            return
        print(f"expected: {fragment}, actual: {contents}")
        if contents != fragment:
            # Send error
            requests.post(API_LOC,
                          data={'token': TAPD_TOKEN, 'hostname': TAPD_HOSTNAME, 'success': False, 'error_code': 'auth',
                                'extra': {'failed_sector': i}, 'csrfmiddlewaretoken': csrftoken})
            print("Errored! @ verification error")
            return
    print("Success!")
    requests.post(API_LOC,
                  data={'token': TAPD_TOKEN, 'hostname': TAPD_HOSTNAME, 'success': True, 'error_code': 'unknown',
                        'extra': {}, 'csrfmiddlewaretoken': csrftoken})


def main():
    monitor = CardMonitor()
    observer = TapObserver(handle_card)
    monitor.addObserver(observer)
    try:
        while True:
            time.sleep(5)
    finally:
        monitor.deleteObserver(observer)


if __name__ == '__main__':
    main()
