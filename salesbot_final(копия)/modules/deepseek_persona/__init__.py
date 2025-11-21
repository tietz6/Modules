# Module-level init for deepseek_persona
# Exposes the register_telegram function for the telegram autoloader

try:
    # Import register_telegram from the current version
    from ._current import register_telegram
    __all__ = ['register_telegram']
except ImportError:
    # Fallback to v1 if _current is not available
    try:
        from .v1 import register_telegram
        __all__ = ['register_telegram']
    except ImportError:
        # If neither version has register_telegram, module won't register telegram handlers
        pass
