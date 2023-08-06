import random, time, gevent

class SecretManager:
    def __init__(self, registry, obj, lifetime, secret = None):
        self.registry = registry
        self.obj = obj
        if secret is None:
            secret = random.getrandbits(32)
        self.secret = secret
        self.lifetime = lifetime
    def live_and_die(self):
        gevent.sleep(self.lifetime)
        self.registry.remove(self.secret)

class SecretsRegistry:
    def __init__(self, default_lifetime):
        self.secrets = {}
        self.default_lifetime = default_lifetime
    def generate_secret(self, obj, lifetime = None, secret = None):
        if secret is None and lifetime is None:
            lifetime = self.default_lifetime
        sec = SecretManager(self, obj, lifetime, secret)
        self.secrets[sec.secret] = sec
        if lifetime is not None:
            gevent.Greenlet.spawn(sec.live_and_die)
        return sec.secret
    def get_obj(self, secret):
        sec = self.secrets.get(secret, None)
        if sec is not None:
            return sec.obj
    def remove(self, secret):
        del self.secrets[secret]
    def pop_object(self, secret):
        obj = self.get_obj(secret)
        if obj is not None:
            del self.secrets[secret]
        return obj
