import os
import redis
redis_host=os.environ.get("REDIS_HOST") or "localhost"
redis_port=os.environ.get("REDIS_PORT") or 6379
redis_client=redis.Redis(host=redis_host, port=redis_port,decode_responses=True)