import json
import redis


class RedisDB(object):

    def __init__(self, db, *args, **kwargs):
        self.db = db

    @classmethod
    def from_url(cls, url, *args, **kwargs):
        return cls(redis.from_url(url), *args, **kwargs)

    @property
    def keys(self):
        keys = [k.decode() for k in self.db.keys()]
        return list(filter(lambda k: k.startswith(self._prefix), keys))

    @property
    def _prefix(self):
        return ""

    def _key_with_prefix(self, key):
        key = str(key)
        if not key.startswith(self._prefix):
            key = self._prefix + key
        return key

    def _key_without_prefix(self, key):
        if key.startswith(self._prefix):
            key = key[len(self._prefix):]
        return key

    def __contains__(self, key):
        return self.db.exists(self._key_with_prefix(key))

    def __getitem__(self, key):
        result = self.db.get(self._key_with_prefix(key))
        if result:
            return json.loads(result.decode())
        return {}

    def add(self, key, info=None):
        user_info = RedisDB.__getitem__(self, key) or {}
        user_info.update(info or {})
        self.db.set(self._key_with_prefix(key), json.dumps(user_info))

    def to_dict(self):
        return {key: self[key] for key in self.keys}

    def to_json(self, filename):
        result = self.to_dict()
        json.dump(result, open(filename, "w"), sort_keys=True, indent=2)

    def from_json(self, filename):
        result = json.load(open(filename, "r"))
        for key, info in result.items():
            if key.startswith(self._prefix):
                self.add(key, info)
