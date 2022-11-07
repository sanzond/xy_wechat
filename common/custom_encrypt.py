import hashlib
import random

salt_list = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_str():
    salt = ''
    for i in range(16):
        salt += random.choice(salt_list)
    return salt


class CustomEncrypt(object):
    """
    custom encrypt, use md5 to encrypt password, and add salt to password. has not decrypt function
    """
    salt = get_random_str()

    @staticmethod
    def encrypt(password):
        obj = hashlib.md5(CustomEncrypt.salt.encode("utf-8"))
        obj.update(password.encode('utf-8'))
        return obj.hexdigest()

    @staticmethod
    def is_equal(password, encode_password):
        return CustomEncrypt.encrypt(password) == encode_password
