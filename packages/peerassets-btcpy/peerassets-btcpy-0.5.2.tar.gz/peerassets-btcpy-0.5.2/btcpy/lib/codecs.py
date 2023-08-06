# Copyright (C) 2017 chainside srl
#
# This file is part of the btcpy package.
#
# It is subject to the license terms in the LICENSE.md file found in the top-level
# directory of this distribution.
#
# No part of btcpy, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE.md file.

from abc import ABCMeta, abstractmethod
from .base58 import b58encode_check, b58decode_check

from .bech32 import decode, encode
from ..structs.address import Address, P2pkhAddress, P2shAddress, P2wpkhAddress, P2wshAddress


class CouldNotDecode(ValueError):
    pass


class CouldNotEncode(ValueError):
    pass


class Codec(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def encode(address: Address) -> str:
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def decode(string: str, strict=None) -> Address:
        raise NotImplemented


class Base58Codec(Codec):

    hash_len = 20

    @staticmethod
    def encode(address):
        try:
            prefix = address.network.base58_raw_prefixes[address.get_type()]
        except KeyError:
            raise CouldNotEncode('Impossible to encode address type: {}, network: {}'.format(address.get_type(),
                                                                                             address.network))
        return b58encode_check(bytes(prefix + address.hash))

    @staticmethod
    def decode(network, string):

        try:
            addr_type = network.base58_prefixes[string[0]]
        except KeyError:
            raise CouldNotDecode('Impossible to decode address {}'.format(string))
        hashed_data = bytearray(b58decode_check(string))[1:]

        if len(hashed_data) != Base58Codec.hash_len:
            raise CouldNotDecode('Data of the wrong length: {}, expected {}'.format(len(hashed_data),
                                                                                    Base58Codec.hash_len))
        if addr_type == 'p2pkh':
            cls = P2pkhAddress
        elif addr_type == 'p2sh':
            cls = P2shAddress
        else:
            raise ValueError('Unknown address type: {}'.format(addr_type))

        return cls(network, hashed_data)


class Bech32Codec(Codec):

    lengths = {42: 'p2wpkh',
               62: 'p2wsh'}

    @staticmethod
    def encode(address):
        return encode(address.network.hrp, address.version, address.hash)

    @staticmethod
    def decode(network, string):

        if not string:
            raise CouldNotDecode('Impossible to decode empty string')

        lower = string[0].islower()
        for char in string:
            if not char.isdigit() and char.islower() != lower:
                raise CouldNotDecode('String {} mixes upper- and lower-case characters'.format(string))

        string = string.lower()
    
        if string[:2] != network.bech32_hrp:
            raise CouldNotDecode('Impossible to decode address {}'.format(string))

        try:
            addr_type = Bech32Codec.lengths[len(string)]
        except KeyError:
            raise CouldNotDecode('Impossible to decode address {}'.format(string))
        version, hashed_data = decode(string[:2], string)

        if not hashed_data:
            raise CouldNotDecode('Empty hash')

        if addr_type == 'p2wpkh':
            cls = P2wpkhAddress
        elif addr_type == 'p2wsh':
            cls = P2wshAddress
        else:
            raise ValueError('Unknown address type: {}'.format(addr_type))

        return cls(network, bytearray(hashed_data), version)
