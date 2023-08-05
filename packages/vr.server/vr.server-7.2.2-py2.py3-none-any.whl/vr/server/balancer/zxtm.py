import warnings

from vr.common.balancer.stingray import StingrayBalancer as ZXTMBalancer

warnings.warn("This module is deprecated", DeprecationWarning)

__all__ = ['ZXTMBalancer']
