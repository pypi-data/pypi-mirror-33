# -*- coding: latin-1 -*-
# this is ascii, no unicode in this document
from .framework import SanicPluginsFramework
from .plugin import SanicPlugin

__version__ = '0.6.1.dev20180616'
__all__ = ["SanicPlugin", "SanicPluginsFramework", "__version__"]
