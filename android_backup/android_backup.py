#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: Apache-2.0
import tarfile
import zlib
import enum
import io
import pickle
import os
import getpass
import binascii
import sys

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto import Random
except ImportError:
    AES = None


class CompressionType(enum.IntEnum):
    NONE = 0
    ZLIB = 1


class EncryptionType(enum.Enum):
    NONE = 'none'
    AES256 = 'AES-256'


class Proxy:
    """
    Proxy class for applying a transformer function around each read call
    """
    def __init__(self, transformer, source, chunk_size=4096):
        self.transformer = transformer
        self.source = source
        self.pos = 0
        self._buffer = bytearray()
        self.chunk_size = chunk_size

    def read(self, n=0):
        data = self._buffer
        if len(data) < n:
            for chunk in iter(lambda: self.source.read(self.chunk_size), b''):
                res = self.transformer(chunk)
                if not res:
                    break
                data.extend(res)
                if n and len(data) >= n:
                    break
            else:
                pass
                #raise IOError("No data after {} bytes, was expecting another {} bytes".format(self.pos, n - len(data)))

        if len(data) > n:
            self._buffer = data[n:]
            data = data[:n]
        else:
            self._buffer = bytearray()

        self.pos += len(data)
        return bytes(data)

    def tell(self):
        return self.pos


class AndroidBackup:
    """
    Handles android backup files (.ab).

    Supports compression and AES encryption (via pycrypto)

    >>> with AndroidBackup('backup.ab') as ab:
    >>>   ab.list()
    """
    def __init__(self, fname=None, password=None, stream=True):
        """
        :param fname: The filename of the backup file or a file-like object
        :param password: The password to use for the en-/decryption
        :param stream: Open the backup file in stream mode. Reduces memory usage
                       but allows only sequential reads. Default: True 
        """
        self.fname = 'unknown'
        self.fp = None
        self.version = None
        self.compression = None
        self.encryption = None
        self.stream = stream
        self.password = password
        # position of the actual file data (after the header)
        self.__data_start = 0

        if isinstance(fname, str):
            self.open(fname)
            self.fname = fname
        else:
            self.fp = fname
            if hasattr(self.fp, 'name'):
                self.fname = self.fp.name

    def open(self, fname, mode='rb'):
        """
        (Re-)opens a backup file
        """
        self.close()
        self.fp = open(fname, mode)
        self.fname = fname

    def close(self):
        """
        Closes the filedescriptor for a backup file
        """
        if self.fp is not None:
            self.fp.close()

    def is_encrypted(self):
        """
        Returns True if the header indicates an encryption scheme
        """
        return self.encryption == EncryptionType.AES256
    
    def parse(self):
        """
        Parses a backup file header. Will be done automatically if
        used together with the 'with' statement
        """
        self.fp.seek(0)
        magic = self.fp.readline()
        assert magic == b'ANDROID BACKUP\n'
        self.version = int(self.fp.readline().strip())
        self.compression = CompressionType(int(self.fp.readline().strip()))
        self.encryption = EncryptionType(self.fp.readline().strip().decode())
        self.__data_start = self.fp.tell()

    def __str__(self):
        return '\n'.join([
            "Version: {}".format(self.version),
            "Compression: {}".format(self.compression),
            "Encryption: {}".format(self.encryption),
        ])

    def _decrypt(self, fp, password=None):
        """
        Internal decryption function

        Uses either the password argument for the decryption,
        or, if not supplied, the password field of the object

        :param fp: a file object or similar which supports the readline and read methods
        :rtype: Proxy
        """
        if AES is None:
            raise ImportError("PyCrypto required")
        
        if password is None:
            password = self.password

        if password is None:
            raise ValueError(
                "Password need to be provided to extract encrypted archives")

        # read the PBKDF2 parameters
        # salt
        user_salt = fp.readline().strip()
        user_salt = binascii.a2b_hex(user_salt)
        # checksum salt
        ck_salt = fp.readline().strip()
        ck_salt = binascii.a2b_hex(ck_salt)
        # hashing rounds
        rounds = fp.readline().strip()
        rounds = int(rounds)
        # encryption IV
        iv = fp.readline().strip()
        iv = binascii.a2b_hex(iv)
        # encrypted master key
        master_key = fp.readline().strip()
        master_key = binascii.a2b_hex(master_key)

        # generate key for decrypting the master key
        user_key = PBKDF2(password, user_salt, dkLen=256 // 8, count=rounds)
        # decrypt the master key and iv
        cipher = AES.new(user_key,
                         mode=AES.MODE_CBC,
                         IV=iv)
        master_key = bytearray(cipher.decrypt(master_key))
        # format: <len IV: 1 byte><IV: n bytes><len key: 1 byte><key: m bytes><len checksum: 1 byte><checksum: k bytes>
        # get IV
        l = master_key.pop(0)
        master_iv = bytes(master_key[:l])
        master_key = master_key[l:]
        # get key
        l = master_key.pop(0)
        mk = bytes(master_key[:l])
        master_key = master_key[l:]
        # get checksum
        l = master_key.pop(0)
        master_ck = bytes(master_key[:l])

        # double encode utf8
        utf8mk = self.encode_utf8(mk)
        # calculate checksum by using PBKDF2
        calc_ck = PBKDF2(utf8mk, ck_salt, dkLen=256//8, count=rounds)
        assert calc_ck == master_ck
        # install decryption key
        cipher = AES.new(mk,
                         mode=AES.MODE_CBC,
                         IV=master_iv)

        off = fp.tell()
        fp.seek(0, 2)
        length = fp.tell() - off
        fp.seek(off)

        if self.stream:
            # decryption transformer for Proxy class
            def decrypt(data):
                data = bytearray(cipher.decrypt(data))

                if fp.tell() - off >= length:
                    # check padding (PKCS#7)
                    pad = data[-1]
                    assert data.endswith(bytearray([pad] * pad)), "Expected {!r} got {!r}".format(bytearray([pad] * pad), data[-pad:])
                    data = data[:-pad]

                return data

            return Proxy(decrypt, fp, cipher.block_size)
        else:
            data = bytearray(cipher.decrypt(fp.read()))
            pad = data[-1]
            assert data.endswith(bytearray([pad] * pad)), "Expected {!r} got {!r}".format(bytearray([pad] * pad), data[-pad:])
            data = data[:-pad]
            return io.BytesIO(data)

    @staticmethod
    def encode_utf8(mk):
        """
        (Double-)encodes the given string (masterkey) with utf-8

        Tries to behave like the Java implementation
        """
        utf8mk = mk.decode('raw_unicode_escape')
        utf8mk = list(utf8mk)
        to_char = chr
        if sys.version_info[0] < 3:
            to_char = unichr
        for i in range(len(utf8mk)):
            c = ord(utf8mk[i])
            # fix java encoding (add 0xFF00 to non ascii chars)
            if 0x7f < c < 0x100:
                c += 0xff00
                utf8mk[i] = to_char(c)
        return ''.join(utf8mk).encode('utf-8')

    def _encrypt(self, dec, password=None):
        """
        Internal encryption function

        Uses either the password argument for the encryption,
        or, if not supplied, the password field of the object

        :param dec: a byte string representing the to be encrypted data
        :rtype: bytes
        """
        if AES is None:
            raise ImportError("PyCrypto required")

        if password is None:
            password = self.password

        if password is None:
            raise ValueError(
                "Password need to be provided to create encrypted archives")

        # generate the different encryption parts (non-secure!)
        master_key = Random.get_random_bytes(32)
        master_salt = Random.get_random_bytes(64)
        user_salt = Random.get_random_bytes(64)
        master_iv = Random.get_random_bytes(16)
        user_iv = Random.get_random_bytes(16)
        rounds = 10000

        # create the PKCS#7 padding
        l = len(dec)
        pad = 16 - (l % 16)
        dec += bytes([pad] * pad)

        # encrypt the data
        cipher = AES.new(master_key, IV=master_iv, mode=AES.MODE_CBC)
        enc = cipher.encrypt(dec)

        # generate the master key checksum
        master_ck = PBKDF2(self.encode_utf8(master_key),
                           master_salt, dkLen=256//8, count=rounds)

        # generate the user key from the given password
        user_key = PBKDF2(password,
                          user_salt, dkLen=256//8, count=rounds)

        # encrypt the master key and iv
        master_dec = b"\x10" + master_iv + b"\x20" + master_key + b"\x20" + master_ck
        l = len(master_dec)
        pad = 16 - (l % 16)
        master_dec += bytes([pad] * pad)
        cipher = AES.new(user_key, IV=user_iv, mode=AES.MODE_CBC)
        master_enc = cipher.encrypt(master_dec)

        # put everything together
        enc = binascii.b2a_hex(user_salt).upper() + b"\n" + \
                binascii.b2a_hex(master_salt).upper() + b"\n" + \
                str(rounds).encode() + b"\n" + \
                binascii.b2a_hex(user_iv).upper() + b"\n" + \
                binascii.b2a_hex(master_enc).upper() + b"\n" + enc

        return enc

    def _decompress(self, fp):
        """
        Internal function for decompressing a backup file with the DEFLATE algorithm

        :rtype: Proxy
        """
        decompressor = zlib.decompressobj()
        if self.stream:
            return Proxy(decompressor.decompress, fp)
        else:
            out = io.BytesIO(decompressor.decompress(fp.read()))
            out.write(decompressor.flush())
            out.seek(0)
            return out

    def read_data(self, password=None):
        """
        Helper function which decrypts and decompresses the data if necessary
        and returns a tarfile.TarFile to interact with
        """
        fp = self.fp
        fp.seek(self.__data_start)

        if self.is_encrypted():
            fp = self._decrypt(fp, password=password)

        if self.compression == CompressionType.ZLIB:
            fp = self._decompress(fp)

        if self.stream:
            mode = 'r|*'
        else:
            mode = 'r:*'
        tar = tarfile.open(fileobj=fp, mode=mode)
        return tar

    def unpack(self, target_dir=None, password=None, pickle_fname=None):
        """
        High level function for unpacking a backup file into the given
        target directory (will be generated based on the filename if not given).

        Creates also a filename.pickle file containing the exact order of the included files
        (required for repacking).

        :param target_dir: the directory to extract the backup file into
                           (default: filename + _unpacked)
        :param password: optional password for decrypting the backup
                         (can also be set in the constructor)
        """

        if target_dir is None:
           target_dir = os.path.basename(self.fname) + '_unpacked'
        if pickle_fname is None:
            pickle_fname = os.path.basename(self.fname) + '.pickle'
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        tar = self.read_data(password)
        members = tar.getmembers()

        # reopen stream (TarFile is not able to seek)
        tar = self.read_data(password)

        tar.extractall(path=target_dir, members=members)

        with open(pickle_fname, 'wb') as fp:
            pickle.dump(members, fp)

    def list(self, password=None):
        """
        Lists the content of the backup to stdout
        """
        tar = self.read_data(password)
        tar.list()

    def get_files(self, password=None):
        """
        Returns the content of the backup file
        """
        tar = self.read_data(password)
        return tar.getmembers()

    def pack(self, fname, source_dir=None, password=None, pickle_fname=None):
        """
        High level function for repacking a backup file from the given
        target directory (will be generated based on the filename if not given).

        Requires also a filename.pickle file which was generated during the unpacking
        step.

        The fields `version`, `compression` and `encryption` have to be set before calling
        this method.

        :param source_dir: the directory to create the backup file from
                           (default: filename + _unpacked)
        :param password: optional password for decrypting the backup
                         (can also be set in the constructor)
        """
        if source_dir is None:
            source_dir = os.path.basename(fname) + '_unpacked'
        if pickle_fname is None:
            pickle_fname = os.path.basename(fname) + '.pickle'

        assert self.version is not None, "Backup version is not set"
        assert self.compression is not None, "Compression level is not set"
        assert self.encryption is not None, "Encryption level is not set"

        data = io.BytesIO()
        tar = tarfile.TarFile(name=fname,
                              fileobj=data,
                              mode='w',
                              format=tarfile.PAX_FORMAT)

        with open(pickle_fname, 'rb') as fp:
            members = pickle.load(fp)

        with open(fname, 'wb') as fp:
            os.chdir(source_dir)
            for member in members:
                if member.isreg():
                    tar.addfile(member, open(member.name, 'rb'))
                else:
                    tar.addfile(member)

            tar.close()

            data.seek(0)
            if self.compression == CompressionType.ZLIB:
                compressor = zlib.compressobj(method=zlib.DEFLATED)
                data = compressor.compress(data.read()) + compressor.flush()
            if self.is_encrypted():
                data = self._encrypt(data, password=password)
        
            fp.write(b'ANDROID BACKUP\n')
            fp.write('{}\n'.format(self.version).encode())
            fp.write('{:d}\n'.format(self.compression).encode())
            fp.write('{}\n'.format(self.encryption.value).encode())

            fp.write(data)

    def __exit__(self, *args, **kwargs):
        self.close()

    def __enter__(self):
        self.parse()
        return self
