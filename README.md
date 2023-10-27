# ratelimit_requests_cache
*Ratelimit requests in Python, but only if they're not served from the cache*

This package combines the best bits of the [`ratelimit`](https://pypi.org/project/ratelimit) module and the [`requests_cache`](https://pypi.org/project/requests_cache) module.
It will rate limit outgoing requests, but not count invocations if a request can be served from the cache.

## Usage

```python
import requests
import requests_cache
from ratelimit import sleep_and_retry
from ratelimit_requests_cache import limits_if_not_cached


@sleep_and_retry
@limits_if_not_cached(calls=1, period=1)
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
```

## Installation
```bash
python3 -m pip install ratelimit_requests_cache
```