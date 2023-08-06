from applauncher.kernel import ConfigurationReadyEvent
import redis


class RedisBundle(object):
    def __init__(self):

        self.config_mapping = {
            'redis': {
                'host': {'type': 'string', 'default': 'localhost'},
                'port': {'type': 'integer', 'default': 6379},
                'db': {'type': 'integer', 'default': 0},
                'password': {'type': 'string', 'nullable': True},
                'socket_timeout': {'type': 'integer', 'nullable': True},
                'socket_connect_timeout': {'type': 'integer', 'nullable': True},
                'socket_keepalive': {'type': 'boolean', 'nullable': True},
                'socket_keepalive_options': {'nullable': True},
                'connection_pool': {'nullable': True},
                'unix_socket_path': {'nullable': True},
                'encoding': {'type': 'string', 'default': 'utf-8'},
                'encoding_errors': {'type': 'string', 'default': 'strict'},
                'charset': {'nullable': True},
                'errors': {'nullable': True},
                'decode_responses': {'type': 'boolean', 'default': False},
                'retry_on_timeout': {'type': 'boolean', 'default': False},
                'ssl': {'type': 'boolean', 'default': False},
                'ssl_keyfile': {'nullable': True},
                'ssl_certfile': {'nullable': True},
                'ssl_cert_reqs': {'nullable': True},
                'ssl_ca_certs': {'nullable': True},
                'max_connections': {'type': 'integer', 'nullable': True}
            }
        }

        self.injection_bindings = {}

        self.event_listeners = [
            (ConfigurationReadyEvent, self.config_ready)
        ]

    def config_ready(self, event):
        d = dict(event.configuration.redis._asdict())
        for i in d:
            if hasattr(d[i], "_asdict"):
                d[i] = None

        self.injection_bindings[redis.Redis] = redis.Redis(**d)

