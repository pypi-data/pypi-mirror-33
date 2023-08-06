"""
dxl.core.logger utilities is providing a AOP 范式 logger, 
based on standard logging system.

Objective:
- clear code base with AOP
- advantages from standard logging system
"""
from ._logger import Logger
from .backend import SimpleInMemoryBackend
