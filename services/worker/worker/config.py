import os


BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")