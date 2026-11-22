import time
from functools import wraps

def cached(ttl):
    store = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args[1:], tuple(sorted(kwargs.items())))                   
            now = time.monotonic()
            hit = store.get(key)
            if hit is not None and hit[0] > now:
                return hit[1]
            value = await func(*args, **kwargs)
            store[key] = (now + ttl, value)    
            return value
        return wrapper
    return decorator

