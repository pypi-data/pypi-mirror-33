import warnings

from vr.common.balancer.dummy import DummyBalancer

warnings.warn("This module is deprecated", DeprecationWarning)

__all__ = ['DummyBalancer']
