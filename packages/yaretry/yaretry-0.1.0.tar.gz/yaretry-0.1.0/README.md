# yaretry - Yet Another Retry Library

This is a small python library for wrapping or decorating functions with retrying logic.

## Naive Usage

Wrap any function with the default retrying logic:

```python

import yaretry

...

retrying_f = yaretry.wrap(f)
res = retrying_f(call, with, normal, params)
```

Decorate a function with the default retrying logic:

```python

@yaretry.decorate()
def foo(bar):
   pass


foo()
```

The default retrying logic will retry calling the function, as long as it raises an instanceof Exception, and will wait an exponentially growing delay between each call. The initial delay will be 1 second, and will double itself every time.

## Customizing Retrying Logic

The `yaretry` library comes with a Params class, that can be passed to the wrapper and decorator, to customize the retrying logic.

To add a timeout, measured in seconds:

```
retrying_f = yaretry.wrap(f, yaretry.Params(timeout=60))
```

To add a maximum number of retry attempts:

```
retrying_f = yaretry.wrap(f, yaretry.Params(max_attempts=10))
```

To change the initial delay, and the exponent:

```
retrying_f = yaretry.wrap(f, yaretry.Params(intial_delay=0.5, exponent=1.2))

# make the delay constant:
retrying_f = yaretry.wrap(f, yaretry.Params(intial_delay=10, exponent=1))
```

To retry in case the function returns False (or a value that, when cast to bool will be False):
```
@yaretry.decorate(yaretry.Params(retry_on_false=True))
def foo(bar):
    if bar == 1:
        return False  # will retry
    elif bar == 2:
        return None   # will retry
    elif bar == 3:
        return "False"  # will *not* retry
    else:
        return True
```

To retry only in case of a specific exception or several exceptions:
```
@yaretry.decorate(yaretry.Params(allowed_exceptions=(
    MyCustomException,
    LookupError))
def foo(bar):
    if bar == 1:
        raise MyCustomException()  # will retry
    elif bar == 2:
        raise Exception()  # will not retry and raise the Exception
    else:
        raise KeyError()  # will retry, as KeyError subclasses LookupError
```

The full list of parameters to customize:

- *timeout* - number of seconds after which retrying will stop
- *max_attempts* - the number of attempts to retry calling the function, before giving up
- *initial_delay* - the number of seconds to wait before the first retry
- *max_delay* - the largest delay to wait between retries
- *exponent* - from retry to retry, the delay is multiplied by this number
- *logger* - use the provided logger to log when a retry is performed
- *raise_last_exception* - if True, after retrying is done, the last exception thrown will be raised. if False (the default), the first exception thrown is raised.
- *retry_on_false* - retry calling the function if it returns a value which `bool(value) == False`
- *allowed_exceptions* - a tuple of exception classes which, when thrown, the function will be retried
- *should_retry_cb* - a callback which will be called with the thrown exception. If the callback returns True, the function will be retried
- *log_level* - a logging.XXXXX log level, indicating which log level to use when logging retry attempts


## Some more examples

Pass a callback to retry only on HTTP 5xx Errors

```python
import yaretry
import requests

def is_server_or_connection_error(ex):
    if isinstance(ex, requests.exceptions.HTTPError):
        return ex.response.status_code >= 500
    if isinstance(ex, requests.exceptions.ConnectionError):
        return True
    return False


@yaretry.decorate(yaretry.Params(
    max_attempts=5,
    should_retry_cb=is_server_or_connection_error))
def call_api(url):
    res = requests.get(url)
    res.raise_on_failure()
    return res.json()
```
