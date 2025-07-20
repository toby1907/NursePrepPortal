from django.core.management.base import BaseCommand
from base.models import Session, Candidate, ProcedureStation

class Command(BaseCommand):
    help = 'Assign all candidates in a session to all stations in that session'

    def add_arguments(self, parser):
        parser.add_argument('session_id', type=int, help='ID of the session')

    def handle(self, *args, **kwargs):
        session_id = kwargs['session_id']
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            self.stdout.write(self.style.ERROR('Session not found.'))
            return

        candidates = session.candidates.all()
        stations = session.procedure_stations.all()

        for station in stations:
            station.candidates.add(*candidates)

        self.stdout.write(self.style.SUCCESS(
            f"Assigned {candidates.count()} candidates to {stations.count()} stations in session '{session.name}'."
        ))
