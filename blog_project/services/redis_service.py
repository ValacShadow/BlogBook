import redis
import os

# Set the Redis host and port to connect to the local server
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # Test connection
    redis_client.ping()
    print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis at {REDIS_HOST}:{REDIS_PORT} - {e}")
except Exception as e:
    print(f"An error occurred: {e}")
