import six
import pickle
from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT
from django.core.cache.backends.locmem import LocMemCache
from django.conf import settings
from django_redis import get_redis_connection
from django_redis.cache import RedisCache


class StellaCacheMixin(object):
    CHEAP_EXISTS = False

    @classmethod
    def make_tag_key(cls, tag):
        if isinstance(tag, six.string_types):
            tag = tag
        elif isinstance(tag, int):
            tag = str(tag)
        else:
            raise NotImplementedError('Tag must be int or str')

        return tag

    def hset(self, name, key, value):
        raise NotImplementedError

    def hdel(self, name, key):
        raise NotImplementedError

    def hget(self, name, key):
        raise NotImplementedError

    def sadd(self, key, value):
        raise NotImplementedError

    def set(self, key, value, timeout=None, tags=None):
        if callable(value):
            raise Exception('Can\'t use callable')
        super(PowerCacheMixin, self).set(key, value, timeout)
        if tags is not None:
            for tag in tags:
                self.sadd(self.make_tag_key(tag), key)

    def _get_tagged_keys(self, tag):
        keys = self.get(self.make_tag_key(tag)) or []
        return keys

    def delete_by_tags(self, *tags):
        all_keys = set()
        for tag in tags:
            all_keys.update(self._get_tagged_keys(tag))
        self.delete_many(all_keys)

    def delete_many(self, *args, **kwargs):
        super().delete_many(*args, **kwargs)


class StellaCache(RedisCache):
    @classmethod
    def make_tag_key(cls, tag):
        if isinstance(tag, six.string_types):
            tag = tag
        elif isinstance(tag, int):
            tag = str(tag)
        else:
            raise NotImplementedError('Tag must be int or str')

        return tag

    def get_raw_client(self):
        return get_redis_connection('default')

    def sadd(self, key, value):
        client = self.get_raw_client()
        return client.sadd(key, value)

    def hset(self, name, key, value):
        client = self.get_raw_client()
        named_key = self.make_key(name)
        pversion = self.pickle_version
        r = client.hset(
            named_key, key, pickle.dumps(value, protocol=pversion))
        return r

    def hdel(self, name, key):
        client = self.get_raw_client()
        named_key = self.make_key(name)
        return client.hdel(named_key, key)

    def hget(self, name, key):
        client = self.get_raw_client()
        named_key = self.make_key(name)
        r = client.hget(named_key, key)
        if r is not None:
            r = pickle.loads(r)
        return r

    @staticmethod
    def _chunk_keys(keys, chunk_size):
        """Yield successive chunks from keys."""
        keys = list(keys)
        for i in range(0, len(keys), chunk_size):
            yield keys[i:i + chunk_size]

    def delete_by_tags(self, *tags, chunk_size=None):
        """
        Delete the cache of a number of tags. This is done in chunks to avoid
        redis timeouts.
        """
        if not tags:
            return

        client = self.get_raw_client()
        tag_keys = {self.make_tag_key(tag) for tag in tags}
        keys = client.sunion(tag_keys)
        keys = {k.decode('utf-8') for k in keys}
        all_keys = keys | tag_keys

        chunk_size = chunk_size or settings.CACHE_DEFAULT_DELETE_CHUNK_SIZE
        for chunk in self._chunk_keys(all_keys, chunk_size):
            self.delete_many(chunk)


class BaseLocMemPowerCache(PowerCacheMixin):
    CHEAP_EXISTS = True

    def sadd(self, key, value):
        d = self.get(key, set())
        d.add(value)
        return self.set(key, d, settings.CACHE_EXPIRATION)

    def hset(self, name, key, value):
        d = self.get(name, {})
        d[key] = value
        return self.set(name, d, settings.CACHE_EXPIRATION)

    def hdel(self, name, key):
        d = self.get(name, {})
        d.pop(key, None)
        return self.set(name, d, settings.CACHE_EXPIRATION)

    def hget(self, name, key):
        d = self.get(name, {})
        return d.get(key, None)


class LocMemPowerCache(BaseLocMemPowerCache, LocMemCache):
    pass


class BaseLocMemThreadOnly(BaseCache, local):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(BaseLocMemThreadOnly, self).__init__(*args, **kwargs)
        self._cache = {}
        self.hard_reset()

    def hard_reset(self):
        self._cache = {}

    def set(self, key, value, tags=None, timeout=DEFAULT_TIMEOUT,
            version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._set(key, value, timeout)

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT):
        self._cache[key] = value

    def incr(self, key, delta=1, version=None):
        value = self.get(key, version=version, acquire_lock=False)
        if value is None:
            raise ValueError("Key '%s' not found" % key)
        new_value = value + delta
        self._cache[key] = new_value
        return new_value

    def get(self, key, default=None, version=None, acquire_lock=True):
        full_key = self.make_key(key, version=version)
        self.validate_key(key)

        if key in self:
            return self._cache[full_key]

        try:
            del self._cache[full_key]
        except KeyError:
            pass
        return default

    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        if not self._has_expired(key):
            return True

        try:
            del self._cache[key]
        except KeyError:
            pass
        return False

    def _has_expired(self, key):
        return key not in self._cache

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass

    def delete(self, key, version=None):
        full_key = self.make_key(key, version=version)
        self.validate_key(full_key)
        self._delete(full_key)

    def clear(self):
        self._cache.clear()


class LocMemThreadOnly(BaseLocMemPowerCache, BaseLocMemThreadOnly):

    pass
