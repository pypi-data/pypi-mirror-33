import hashlib
import logging
import rncryptor
from .base import RedisDB
from .tag import UserInfoEnum


class Cryptor(object):
    def __init__(self, salt):
        self.salt = salt
        if self.salt:
            self.salt = hashlib.sha256(str.encode(self.salt)).hexdigest()
            logging.info("salt is set.")
        else:
            logging.info("No salt provided. It won't be possible to "
                         "decrypt sensitive fields.")
        self.rn_cryptor = rncryptor.RNCryptor()

    def encrypt(self, value):
        bytes_value = self.rn_cryptor.encrypt(value, self.salt)
        return bytes_value.hex()

    def decrypt(self, value):
        bytes_value = bytes.fromhex(value)
        return self.rn_cryptor.decrypt(bytes_value, self.salt)

    def update_sensitive_fields(self, sensitive_fields, info, to_encrypt=True):
        sensitive_fields_in_info = sensitive_fields.intersection(info.keys())
        if not sensitive_fields_in_info or not self.salt:
            return info
        crypt_map = {True: self.encrypt, False: self.decrypt}
        f_crypt = crypt_map[to_encrypt]
        is_encrypted = info.get(UserInfoEnum.IS_KEY_ENCRYPTED.lower(), False)
        if is_encrypted != to_encrypt:
            # to avoid encrypt the same information multiple times
            info_updated = {k: f_crypt(info[k])
                            for k in sensitive_fields_in_info}
            info_updated[UserInfoEnum.IS_KEY_ENCRYPTED.lower()] = to_encrypt
            info.update(info_updated)
        return info


class RedisUsers(RedisDB):

    def __init__(self, db, salt=None):
        super(RedisUsers, self).__init__(db)
        self.cryptor = Cryptor(salt)

    @property
    def _prefix(self):
        return "USER:"

    def add(self, key, info=None):
        info = dict(info or {})
        info = self.cryptor.update_sensitive_fields(
            UserInfoEnum.sensitive_fields(), info, True
        )
        super(RedisUsers, self).add(key, info)

    def __getitem__(self, key):
        info = super(RedisUsers, self).__getitem__(key)
        info = self.cryptor.update_sensitive_fields(
            UserInfoEnum.sensitive_fields(), info, False
        )
        return info

    def iter_active_users(self):
        for key in self.keys:
            info = super(RedisUsers, self).__getitem__(key)
            if info.get(UserInfoEnum.ACTIVE.lower(), False):
                yield int(self._key_without_prefix(key))
