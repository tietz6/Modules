# Re-export from latest version (v1)
try:
    from .v1 import register_telegram
    __all__ = ['register_telegram']
except ImportError:
    pass
