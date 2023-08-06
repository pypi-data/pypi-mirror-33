import time
import functools
import collections
import logging


logger = logging.getLogger(__name__)


# The following cool trick inspired by:
# https://stackoverflow.com/questions/11351032/namedtuple-and-default-values-for-optional-keyword-arguments

__PARAMS_ARGS_N_DEFAULTS = {
    'timeout': None,
    'initial_delay': 1,
    'max_delay': None,
    'exponent': 2,
    'logger': logger,
    'raise_last_exception': False,
    'retry_on_false': False,
    'allowed_exceptions': (Exception, ),
    'should_retry_cb': None,
    'log_level': logging.INFO,
    'max_attempts': None
}
Params = collections.namedtuple('Params', list(__PARAMS_ARGS_N_DEFAULTS.keys()))
Params.__new__.__defaults__ = tuple(Params(**__PARAMS_ARGS_N_DEFAULTS))


DEFAULT_PARAMS = Params()


def __has_not_timed_out(start, attempts, params):
    if params.timeout is not None and time.time() - start >= params.timeout:
        return False
    if params.max_attempts is not None and attempts >= params.max_attempts:
        return False
    return True


def __increase_delay(current_delay, params):
    new_delay = current_delay * params.exponent
    if params.max_delay is not None:
        new_delay = min(params.max_delay, new_delay)
    return new_delay


def wrap(f, params=None):

    if params is None:
        params = DEFAULT_PARAMS

    @functools.wraps(f)
    def retrying_f(*args, **kwargs):
        start = time.time()
        caught_exc = None
        delay = float(params.initial_delay)
        attempts = 0
        while __has_not_timed_out(start, attempts, params):
            attempts += 1
            try:
                ret_val = f(*args, **kwargs)
                if not params.retry_on_false or bool(ret_val):
                    return ret_val
                params.logger.log(params.log_level,
                                  'Function returned a False value. sleep=%f',
                                  delay)
            except params.allowed_exceptions as e:
                params.logger.log(params.log_level,
                                  'Caught exception. sleep=%f, exc=%s',
                                  delay, str(e))
                if caught_exc is None or params.raise_last_exception:
                    caught_exc = e
                if params.should_retry_cb is not None \
                        and not params.should_retry_cb(e):
                    raise
            time.sleep(delay)
            delay = __increase_delay(delay, params)
        if caught_exc is not None:
            params.logger.warning('Function failed with an exception: %s',
                                  str(caught_exc))
            raise caught_exc
        params.logger.warning('Function failed with a Falsey return value')
        return ret_val

    return retrying_f  # true decorator


def decorate(params=None):
    def decorator(f):
        return wrap(f, params)
    return decorator
