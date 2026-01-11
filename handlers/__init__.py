from .start import router as start_router
from .rates import router as rates_router
from .alerts import router as alerts_router
from .admin import router as admin_router

__all__ = ['start_router', 'rates_router', 'alerts_router', 'admin_router']

