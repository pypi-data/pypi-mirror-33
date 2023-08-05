from generic_encoders import Encoder

from generic_encryptors.encryptors.aes_encryptor import AesEncryptor

Encoder.add_encoder(AesEncryptor)
