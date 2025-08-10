from .models import ProcedureStation, Session,GlobalSettings

def global_settings(request):
    """Provides global settings and active filtering"""
    settings = GlobalSettings.objects.first()
    active_session = settings.active_session if settings else None
    active_level = settings.active_level if settings else None
    
    return {
        'global_settings': settings,
        'active_session': active_session,
        'active_level': active_level
    }