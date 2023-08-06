REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
DEFAULT_REDIS_DB = 158
META_DATA_DB = 158


LOCKER_PREFIX = 'haipproxy:lock:'

SQUID_BIN_PATH = '/usr/sbin/squid'  # mac os '/usr/local/sbin/squid'
SQUID_CONF_PATH = '/etc/squid/squid.conf'  # mac os '/usr/local/etc/squid.conf'
SQUID_TEMPLATE_PATH = '/etc/squid/squid.conf.backup'  # mac os /usr/local/etc/squid.conf.backup

DATA_ALL = 'haipproxy:all'

LOWEST_TOTAL_PROXIES = 5


TTL_VALIDATED_RESOURCE = 2  # minutes

# client picks proxies which's response time is between 0 and 5 seconds
LONGEST_RESPONSE_TIME = 10

# client picks proxies which's score is not less than 7
LOWEST_SCORE = 6

# valited queues are zsets.squid and other clients fetch ip resources from them.
VALIDATED_HTTP_QUEUE = 'haipproxy:validated:http'
VALIDATED_HTTPS_QUEUE = 'haipproxy:validated:https'
VALIDATED_WEIBO_QUEUE = 'haipproxy:validated:weibo'
VALIDATED_ZHIHU_QUEUE = 'haipproxy:validated:zhihu'
VALIDATED_AZ_QUEUE = 'haipproxy:validated:az'

# time to life of proxy ip resources
TTL_VALIDATED_RESOURCE = 2  # minutes
TTL_HTTP_QUEUE = 'haipproxy:ttl:http'
TTL_HTTPS_QUEUE = 'haipproxy:ttl:https'
TTL_WEIBO_QUEUE = 'haipproxy:ttl:weibo'
TTL_ZHIHU_QUEUE = 'haipproxy:ttl:zhihu'
TTL_AZ_QUEUE = 'haipproxy:ttl:az'

# queue for proxy speed
SPEED_HTTP_QUEUE = 'haipproxy:speed:http'
SPEED_HTTPS_QUEUE = 'haipproxy:speed:https'
SPEED_WEIBO_QUEUE = 'haipproxy:speed:weibo'
SPEED_ZHIHU_QUEUE = 'haipproxy:speed:zhihu'
SPEED_AZ_QUEUE = 'haipproxy:speed:az'

