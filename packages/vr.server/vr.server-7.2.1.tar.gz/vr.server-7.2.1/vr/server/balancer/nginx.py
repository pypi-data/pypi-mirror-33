import warnings

from vr.common.balancer.nginx import NginxBalancer

warnings.warn("This module is deprecated", DeprecationWarning)

__all__ = ['NginxBalancer']
