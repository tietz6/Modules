# Re-export from latest version (v3)
try:
    from .v3 import register_telegram
    __all__ = ['register_telegram']
except ImportError:
    pass
