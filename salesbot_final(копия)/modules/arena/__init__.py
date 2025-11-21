# Re-export from latest version (v4)
try:
    from .v4 import register_telegram
    __all__ = ['register_telegram']
except ImportError:
    pass
