from haipproxy_client.config.settings import (
    VALIDATED_HTTP_QUEUE,
    VALIDATED_HTTPS_QUEUE,
    VALIDATED_WEIBO_QUEUE,
    VALIDATED_ZHIHU_QUEUE,
    VALIDATED_AZ_QUEUE,
    TTL_HTTP_QUEUE,
    TTL_HTTPS_QUEUE,
    TTL_WEIBO_QUEUE,
    TTL_ZHIHU_QUEUE,
    TTL_AZ_QUEUE,
    SPEED_HTTP_QUEUE,
    SPEED_HTTPS_QUEUE,
    SPEED_WEIBO_QUEUE,
    SPEED_ZHIHU_QUEUE,
    SPEED_AZ_QUEUE
    )

# todo the three maps may be combined in one map
# validator scheduler and clients will fetch proxies from the following queues
SCORE_MAPS = {
    'http': VALIDATED_HTTP_QUEUE,
    'https': VALIDATED_HTTPS_QUEUE,
    'weibo': VALIDATED_WEIBO_QUEUE,
    'zhihu': VALIDATED_ZHIHU_QUEUE,
    'az': VALIDATED_AZ_QUEUE
}

# validator scheduler and clients will fetch proxies from the following queues which are verified recently
TTL_MAPS = {
    'http': TTL_HTTP_QUEUE,
    'https': TTL_HTTPS_QUEUE,
    'weibo': TTL_WEIBO_QUEUE,
    'zhihu': TTL_ZHIHU_QUEUE,
    'az': TTL_AZ_QUEUE,
}

SPEED_MAPS = {
    'http': SPEED_HTTP_QUEUE,
    'https': SPEED_HTTPS_QUEUE,
    'weibo': SPEED_WEIBO_QUEUE,
    'zhihu': SPEED_ZHIHU_QUEUE,
    'az': SPEED_AZ_QUEUE,
}