import redis
from flask import current_app

redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(current_app.config['REDIS_URL'])
    return redis_client