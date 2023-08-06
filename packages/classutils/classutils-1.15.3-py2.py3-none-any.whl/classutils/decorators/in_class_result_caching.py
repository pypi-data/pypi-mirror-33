# -*- coding: utf-8 -*-

import functools
import logging_helper
from timingsutil import Timeout

logging = logging_helper.setup_logging()

CLASS_CACHED_RESULTS = u'_cached_results'
CLASS_CACHED_RESULT_PREFIX = u'_cached_'


def clear_class_cached_results(func):

    @functools.wraps(func)
    def wrapper(self,
                *args,
                **kwargs):

        """ Clears all class cached results.
        """

        self.__dict__[CLASS_CACHED_RESULTS] = {}

        return func(self,
                    *args,
                    **kwargs)

    return wrapper


def get_cache_id(name):
    return u'{prefix}{name}'.format(prefix=CLASS_CACHED_RESULT_PREFIX,
                                    name=name)


def get_cache_key(cache_id,
                  *args,
                  **kwargs):
    return cache_id + str(args) + str(kwargs)


# TODO: make this a decorator
def set_class_cache_result(obj,  # e.g. self
                           name,
                           value,
                           *args,
                           **kwargs):

    cache_id = get_cache_id(name=name)

    cache_key = get_cache_key(cache_id,
                              *args,
                              **kwargs)

    if CLASS_CACHED_RESULTS not in obj.__dict__:
        # Cached results dict does not exist (first cache on this instance)
        obj.__dict__[CLASS_CACHED_RESULTS] = {}

    obj.__dict__[CLASS_CACHED_RESULTS][cache_key] = value


def class_cache_result(_func=None,
                       timeout=0):

    """ This decorator handles any decorator args.

    :param _func:       Possibly the function to be decorated _func's type depends on the usage of the decorator.
                        It's a function if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    :param timeout:     If set to an integer/float value the cached result will only be held for the
                        number of seconds specified.  Default = 0 (no timeout)
    :return:
    """

    def arg_wrapper(func):

        """ This is the real decorator and  will cache the return value of the decorated 
        function for the lifetime of the object.

        NOTE: This should only be used for class functions!
        """
        cache_id = get_cache_id(name=func.__name__)

        timer = Timeout(seconds=timeout,
                        start_in_an_expired_state=True) if timeout > 0 else None

        @functools.wraps(func)
        def wrapper(self,
                    *args,
                    **kwargs):

            """ Simple run time cache for the function result.

            :param self:        As this is for class methods we have to add self.
            :param args:        Args for the function.
            :param kwargs:      Kwargs for the function.  Additional function kwargs made available by decorator:
                                refresh - setting to True will force this cached result to refresh itself.
            :return:            The result of the function.
            """

            # Check refresh param
            refresh = kwargs.get('refresh', False)

            # Ensure refresh is not still in kwargs when passed to function or cache_key generated
            if 'refresh' in kwargs:
                del kwargs['refresh']

            cache_key = get_cache_key(cache_id,
                                      *args,
                                      **kwargs)
            action = u'Caching'

            # Check whether we are using a timeout
            if timer is not None:
                # When the timer expires refresh the cache and restart the timer.
                if timer.expired:
                    refresh = True
                    timer.restart()

            if CLASS_CACHED_RESULTS not in self.__dict__:
                # Cached results dict does not exist (first cache on this instance)
                self.__dict__[CLASS_CACHED_RESULTS] = {}

            try:
                # Attempt to retrieve cached value
                cached_result = self.__dict__[CLASS_CACHED_RESULTS][cache_key]
                action = u'Refreshing'

            except KeyError:
                # Value has not been cached yet
                pass

            else:
                if not refresh:
                    # logging.debug(u'Returning cached result for {id}'.format(id=cache_key))
                    return cached_result

            logging.debug(u'{action} result for {id}'.format(action=action,
                                                             id=cache_key))

            self.__dict__[CLASS_CACHED_RESULTS][cache_key] = func(self,
                                                                  *args,
                                                                  **kwargs)

            return self.__dict__[CLASS_CACHED_RESULTS][cache_key]

        # Return the decorated function
        return wrapper

    # _func's type depends on the usage of the decorator.  It's a function
    # if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    return arg_wrapper if _func is None else arg_wrapper(_func)
