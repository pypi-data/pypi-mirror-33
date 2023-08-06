from .pyError.pyError import ExtendableError


__all__ = ["pyError.pyError"]

_hush_pyflakes = [ExtendableError]

del _hush_pyflakes
