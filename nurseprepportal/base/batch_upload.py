# your_app/batch_upload.py
import csv
import os
from io import TextIOWrapper
from django.core.files import File
from .models import Session, Candidate, ProcedureStation, Activity


def process_candidate_csv(file, session_name):
    session = Session.objects.get(name=session_name)
    reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
    
    for row in reader:
        candidate, created = Candidate.objects.update_or_create(
            matric_number=row['matric_number'],
            defaults={
                'full_name': row['full_name'],
                'session': session,
                'level': int(row['level'])
            }
        )
        
        # Handle passport photo if provided
        if created and row.get('passport_file'):
            photo_path = os.path.join('passports', row['passport_file'])
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    candidate.passport.save(row['passport_file'], File(f))




# batch_upload.py
def process_station_csv(file, session):
    reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
    for row in reader:
        ProcedureStation.objects.update_or_create(
            name=row['name'],
            session=session,
            defaults={
                'description': row.get('description', ''),
                'level': int(row['level']) if row.get('level') else None
            }
        )

def process_activity_csv(file, session):
    reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
    for row in reader:
        station = ProcedureStation.objects.get(
            name=row['station_name'],
            session=session
        )
        Activity.objects.update_or_create(
            station=station,
            description=row['description'],
            defaults= {'max_score': float(row['max_score'])}
        )

def process_simplified_csv(file, session):
    """Process comma-delimited CSV without headers"""
    reader = csv.reader(TextIOWrapper(file, encoding='utf-8-sig'), delimiter=',')


    for row in reader:
        try:
            if len(row) < 3:
                raise ValueError("Row does not have enough columns")

            matric = row[0].replace('/', '')
            Candidate.objects.update_or_create(
                matric_number=matric,
                defaults={
                    'full_name': row[1].strip(),
                    'session': session,
                    'level': int(row[2])
                }
            )
        except Exception as e:
            print(f"Error processing row {row}: {str(e)}")
            continue
