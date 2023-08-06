import zope.event
import applauncher.kernel
import inject
import redis

class RedisManager(object):

    def __init__(self):
        self.redis = None

    def __getattr__(self, attr):
        return self.redis.__getattribute__(attr)


class RedisBundle(object):
    def __init__(self):
        self.config_mapping = {
            "redis": {
                "hostname": 'localhost',
                "port": 6379,
                "database": 0
            }
        }

        zope.event.subscribers.append(self.event_listener)
        self.injection_bindings = {
            RedisManager: RedisManager()
        }

    def event_listener(self, event):
        if isinstance(event, applauncher.kernel.InjectorReadyEvent):
            config = inject.instance(applauncher.kernel.Configuration).redis
            rm = inject.instance(RedisManager)
            rm.redis = redis.StrictRedis(host=config.hostname, port=config.port, db=config.database)

