"""
A small module that combines the best bits of the requests_cache and ratelimit modules.
It offers a similar ratelimiter to the one provided by the ratelimit module,
but this one only counts invocations that can not be served from the local cache.
"""
from functools import wraps

import requests
import requests_cache
from ratelimit import RateLimitException
from ratelimit.decorators import RateLimitDecorator, sleep_and_retry


class RateLimitIfNotCachedDecorator(RateLimitDecorator):
    """
    A modified version of the original RateLimitDecorator by tomasbasham found here:
    https://github.com/tomasbasham/ratelimit/blob/master/ratelimit/decorators.py
    """

    def __init__(self, *a, **k):
        super(RateLimitIfNotCachedDecorator, self).__init__(*a, **k)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                period_remaining = self.period - (self.clock() - self.last_reset)

                # If the time window has elapsed then reset.
                if period_remaining <= 0:
                    self.num_calls = 0
                    self.last_reset = self.clock()

                # Increase the number of attempts to call the function.
                result = func(*args, **kwargs)

                # Only count towards the rate limit if results are not from the cache
                if not result.from_cache:
                    self.num_calls += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls > self.clamped_calls:
                    if self.raise_on_limit:
                        raise RateLimitException('too many calls', period_remaining)
                    return

            return result

        return wrapper


limits_if_not_cached = RateLimitIfNotCachedDecorator


if __name__ == '__main__':
    # Decorate a method to use a cache
    @sleep_and_retry
    @limits_if_not_cached(calls=1, period=1)  # 1 req / s
    def get_from_httpbin(i):
        return requests.get(f'https://httpbin.org/anything?i={i}')
  
    # Enable requests caching
    requests_cache.install_cache()
    
    # Notice that only the first ten requests will be ratelimited to 1 request / second
    # After that, it's a lot quicker since requests can be served from the cache
    # and the ratelimiter does not engage
    for i in range(100):
        get_from_httpbin(i % 10)
        print(i)
