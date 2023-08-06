"""
Module for functions which are related to cryptography and hashing.
"""
import os
import hashlib
import binascii


class Hasher:
    """
    Performs data hashing with needed algorithm, salt size and amount of rounds.
    """
    def __init__(self, data, salt_size=16, algorithm='sha256', rounds=100000):
        """
        Constructor.
        @param data: data to be hashed.
        @param salt_size: size of salt to be generated.
        @param algorithm: algorithm which hashes data (e.g. SHA256).
        @param rounds: amount of hashing rounds.
        """
        self._data_bytes = data.encode()
        self._salt_size = salt_size
        self._salt_bytes = None
        self.generate_salt()
        self._algorithm = algorithm
        self._rounds = rounds

    def generate_salt(self):
        """
        Generates random salt of needed length. It's highly recommended to use
        salt of size 16 or more.
        @return: None.
        """
        self._salt_bytes = os.urandom(self._salt_size)

    def set_salt_size(self, new_size):
        """
        Sets new salt size. By default salt size is 16.
        @param new_size: new salt size.
        @return: None.
        """
        self._salt_size = new_size

    def set_algorithm(self, new_algorithm):
        """
        Sets new hashing algorithm which should be used to hash data.
        @param new_algorithm: hashing algorithm name.
        @return: None
        """
        self._algorithm = new_algorithm

    def set_rounds(self, new_rounds):
        """
        Sets new amount of rounds to be executed in the process of hashing.
        @param new_rounds: new amount of hashing rounds.
        @return: None.
        """
        self._rounds = new_rounds

    def hash(self):
        """
        Generates hash from the input data.
        @return: hashed data.
        """
        hashed_data = hashlib.pbkdf2_hmac(self._algorithm,
                                          self._data_bytes,
                                          self._salt_bytes,
                                          self._rounds)
        return binascii.hexlify(hashed_data)
