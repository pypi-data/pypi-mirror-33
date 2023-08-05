import os
import six
import hmac
import hashlib
import struct

from generic_encoders import Encoder
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class AesEncryptor(Encoder):
  file_suffixes = ['aes']
  inputs = [six.binary_type]
  outputs = six.binary_type
  
  def __init__(self, key, keykey_size=256):
    self.key = key
    super(AesEncryptor, self)

  def _encode(self, data):
    iv = os.urandom(16)
    self.iv = iv
    self.cipher = Cipher(
      algorithms.AES(self.key),
      modes.CBC(iv),
      backend=default_backend())
    encryptor = self.cipher.encryptor()
    padder = padding.PKCS7(self.cipher.algorithm.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    hmac_data = hmac.new(encrypted_data, self.key, hashlib.sha256).digest()
    return (
        struct.pack('i', len(iv)) +
        iv +
        struct.pack('i', len(hmac_data)) +
        hmac_data +
        encrypted_data
      )

  def _decode(self, data):
    iv_length = struct.unpack('i', data[0:4])[0]
    iv = data[4 : iv_length + 4]
    hmac_length = struct.unpack('i', data[iv_length + 4: iv_length + 8])[0]
    hmac_data = data[iv_length + 8: iv_length + 8 + hmac_length]
    data = data[iv_length + 8 + hmac_length:]
    cipher = Cipher(
      algorithms.AES(self.key),
      modes.CBC(iv),
      backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(self.cipher.algorithm.block_size).unpadder()
    data = decryptor.update(data) + decryptor.finalize()
    return unpadder.update(data) + unpadder.finalize()
    
