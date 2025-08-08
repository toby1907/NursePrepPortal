from .models import ProcedureStation, Session

def global_stations(request):
    try:
        current_session = Session.objects.latest('start_date')
        stations = ProcedureStation.objects.filter(session=current_session)
    except Session.DoesNotExist:
        stations = []
        current_session = None

    return {
        'stations': stations,
        'current_session': current_session
    }
