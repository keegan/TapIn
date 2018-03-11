#!/usr/bin/env python3
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from typing import List
import traceback
import os
import requests
import base64
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tapin.settings")
import django

django.setup()
from tapinback.models import TapUser, Client
from django.contrib.auth.models import User

MIFARE_CLASSIC_1K_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A"

CARD_ACL = [0xFF, 0x07, 0x80, 0x69]

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


def write_sector(connection, sector_num: int, key: List[int], data: List[int]):
    """Write the given data to the sector.  You MUST supply exactly enough data to fill the sector!"""
    auth_block = sector_num * 4
    # Authenticate to the sector
    load_key(connection, key)  # load keys
    authenticate(connection, auth_block)  # act upon keys
    # Read the blocks, omitting the key block if the full sector is not requested
    for i in range(4):
        blockid = auth_block + i
        block_data = data[i * 16:(i + 1) * 16]
        write_data(connection, blockid, block_data, auth=True)


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


def handle_card(connection):
    resp = input("Create user (Y/N) >>> ")
    if resp.upper() == "Y":
        u = User()
        uname = input("Enter username >>> ")
        name = input("Enter name >>> ")
        pwd = input("Enter password >>> ")
        u.username = uname
        u.name = name
        u.password = pwd
        u.save()
    else:
        uname = input("Enter existing username to link to >>> ")
        u = User.objects.get(username=uname)
    # user model
    t_user = TapUser()
    t_user.pin = input("Enter pin >>> ")
    t_user.userid = u
    t_user.save()
    # write UID to card
    # its ascii
    uid_str = str(t_user.id)
    sector_data = list((uid_str + ('\0' * 12)).encode("UTF-8"))
    keysec = [0xFF] * 6 + CARD_ACL + [0xFF] * 6
    write_sector(connection, 1, [0xFF] * 6, sector_data + keysec)
    # decode the blockdata and keydata into their respectinv things
    keydata = t_user.keys
    blockdata = t_user.token
    keydata += '=' * (-len(keydata) % 4)
    blockdata += '=' * (-len(blockdata) % 4)
    keydata = list(base64.urlsafe_b64decode(keydata.encode("UTF-8")))
    blockdata = list(base64.urlsafe_b64decode(blockdata.encode("UTF-8")))
    keys = [keydata[i:i + 6] for i in range(0, len(keydata), 6)]
    blocks = [blockdata[i:i + 48] for i in range(0, len(blockdata), 48)]
    for i in range(14):
        sector_key_acl_thing = keys[i] + CARD_ACL + keys[i]
        write_sector(connection, i + 2, [0xFF] * 6, blocks[i] + sector_key_acl_thing)
        print(f"Writing sector {i+2}")


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
