
import csv
import os
from io import TextIOWrapper
from django.core.files import File
from django.shortcuts import get_object_or_404
from .models import Session, Candidate, ProcedureStation, Activity

def process_candidate_csv(file, session, level=None):
    reader = csv.DictReader(TextIOWrapper(file))
    
    for row in reader:
        try:
            # Create candidate with form-selected session/level
            candidate, created = Candidate.objects.update_or_create(
                matric_number=row['matric_number'],
                defaults={
                    'full_name': row['full_name'],
                    'session': session,
                    'level': level or int(row['level']) if row.get('level') else level
                }
            )
            
            # Handle passport photo if provided
            if created and row.get('passport_file'):
                try:
                    with open(row['passport_file'], 'rb') as f:
                        candidate.passport.save(row['passport_file'], File(f))
                except FileNotFoundError:
                    print(f"Passport photo not found: {row['passport_file']}")
                    
        except Exception as e:
            print(f"Error processing candidate {row}: {str(e)}")
            continue

def process_station_csv(file, session, level=None):
    """Process station CSV with optional level"""
    reader = csv.DictReader(TextIOWrapper(file))
    for row in reader:
        try:
            ProcedureStation.objects.update_or_create(
                name=row['name'],
                session=session,
                defaults={
                    'description': row.get('description', ''),
                    'level': level  # From form
                }
            )
        except Exception as e:
            print(f"Error processing station {row}: {str(e)}")
            continue

def process_activity_csv(file, session):
    """Process activities for existing stations"""
    reader = csv.DictReader(TextIOWrapper(file))
    for row in reader:
        try:
            station = get_object_or_404(
                ProcedureStation,
                name=row['station_name'],
                session=session
            )
            Activity.objects.update_or_create(
                station=station,
                description=row['description'],
                defaults={'max_score': float(row['max_score'])}
            )
        except Exception as e:
            print(f"Error processing activity {row}: {str(e)}")
            continue

def process_combined_csv(file, session, level=None):
    """Process combined station/activity CSV with better station handling and validation"""
    try:
        # Read and validate CSV
        reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8-sig'))
        if not reader.fieldnames:
            raise ValueError("Empty file or invalid CSV format")

        # Clean fieldnames
        reader.fieldnames = [f.strip('\ufeff').strip() for f in reader.fieldnames]
        
        # Validate columns
        required_columns = {'station_name', 'activity_description', 'activity_max_score'}
        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # First get all unique stations from the file
        station_rows = {}
        activities = []
        for i, row in enumerate(reader, 1):
            try:
                cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v 
                             for k, v in row.items()}
                
                # Validate required fields
                if not all(cleaned_row.get(col) for col in required_columns):
                    raise ValueError(f"Missing required values in row {i}")
                
                # Collect station info
                station_name = cleaned_row['station_name']
                if station_name not in station_rows:
                    station_rows[station_name] = {
                        'description': cleaned_row.get('station_description', ''),
                        'level': level
                    }
                
                # Collect activity info
                activities.append({
                    'station_name': station_name,
                    'description': cleaned_row['activity_description'],
                    'max_score': float(cleaned_row['activity_max_score'])
                })
                
            except Exception as e:
                print(f"Row {i} failed: {e}\nRow data: {row}")
                continue

        # Bulk create stations that don't exist
        existing_stations = ProcedureStation.objects.filter(
            name__in=station_rows.keys(),
            session=session
        ).values_list('name', flat=True)
        
        stations_to_create = [
            ProcedureStation(
                name=name,
                session=session,
                description=data['description'],
                level=data['level']
            )
            for name, data in station_rows.items()
            if name not in existing_stations
        ]
        
        if stations_to_create:
            ProcedureStation.objects.bulk_create(stations_to_create)
        
        # Get all stations (newly created and existing)
        stations_map = {
            s.name: s for s in ProcedureStation.objects.filter(
                name__in=station_rows.keys(),
                session=session
            )
        }
        
        # Process activities
        for activity in activities:
            try:
                station = stations_map.get(activity['station_name'])
                if not station:
                    print(f"Station not found for activity: {activity}")
                    continue
                    
                Activity.objects.update_or_create(
                    station=station,
                    description=activity['description'],
                    defaults={'max_score': activity['max_score']}
                )
            except Exception as e:
                print(f"Failed to create activity {activity}: {e}")

        return True
        
    except Exception as e:
        print(f"Fatal processing error: {str(e)}")
        return False