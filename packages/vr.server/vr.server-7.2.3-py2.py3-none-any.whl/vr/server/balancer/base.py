import warnings

from vr.common.balancer.base import Balancer, SshBasedBalancer

warnings.warn("This module is deprecated", DeprecationWarning)

__all__ = ['Balancer', 'SshBasedBalancer']
