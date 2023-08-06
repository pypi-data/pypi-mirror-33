'''
Created on 04.01.2016

@author: marscher
'''
from contextlib import contextmanager
import random

import numpy as np


class conditional(object):
    """Wrap another context manager and enter it only if condition is true.
    """

    def __init__(self, condition, contextmanager):
        self.condition = condition
        self.contextmanager = contextmanager

    def __enter__(self):
        if self.condition:
            return self.contextmanager.__enter__()

    def __exit__(self, *args):
        if self.condition:
            return self.contextmanager.__exit__(*args)


@contextmanager
def numpy_random_seed(seed=42):
    """ sets the random seed of numpy within the context.

    Example
    -------
    >>> import numpy as np
    >>> with numpy_random_seed(seed=0):
    ...    np.random.randint(1000)
    684
    """
    old_state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(old_state)


@contextmanager
def random_seed(seed=42):
    """ sets the random seed of Python within the context.

    Example
    -------
    >>> import random
    >>> with random_seed(seed=0):
    ...    random.randint(0, 1000) # doctest: +SKIP
    864
    """
    old_state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(old_state)


@contextmanager
def settings(**kwargs):
    """ apply given PyEMMA config values temporarily within the given context."""
    from pyemma import config

    old_settings = {}
    try:
        # remember old setting, set new one. May raise ValueError, if invalid setting is given.
        for k, v in kwargs.items():
            old_settings[k] = getattr(config, k)
            setattr(config, k, v)
        yield
    finally:
        # restore old settings
        for k, v in old_settings.items():
            setattr(config, k, v)


@contextmanager
def attribute(obj, attr, val):
    previous = getattr(obj, attr)
    setattr(obj, attr, val)
    try:
        yield
    finally:
        setattr(obj, attr, previous)


@contextmanager
def named_temporary_file(mode='w+b', prefix='', suffix='', dir=None):
    from tempfile import NamedTemporaryFile
    ntf = NamedTemporaryFile(mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=False)
    ntf.close()
    try:
        yield ntf.name
    finally:
        import os
        try:
            os.unlink(ntf.name)
        except OSError:
            pass
