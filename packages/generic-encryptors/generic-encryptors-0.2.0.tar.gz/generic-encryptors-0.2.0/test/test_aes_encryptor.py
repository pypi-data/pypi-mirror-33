import unittest

from generic_encryptors import AesEncryptor

class TestAesEncryptor(unittest.TestCase):

    def test_aes_encryptor_encode_decode(self):
      encryptor = AesEncryptor(key=('1' * 32).encode('ascii'))
      msg = b'123in0i1n 0in\x10\x00\x00\x00\x94\xd0z\xa6\xac\x95\xb2\xf5\x10\xfa\xd7\x9c\xf9\x9a\x8a\xd5 \x00\x00\x00\x89K\x9bGuxf8|\xf5\x93\xb6-\xbf\xab\xd0\x15\x99\xae}cu\xceWnE\xfdj7\xb3X_hc\xdao>0\x86\xcf\xecSI^\xe5<\xcfh'
      self.assertEqual(msg,
          encryptor.decode(encryptor.encode(msg)))


if __name__ == '__main__':
    unittest.main()