
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Candidate, Score, ProcedureStation, Activity, Session
from django.db.models import Prefetch
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import redirect

def dashboard(request):
    selected_matric = request.GET.get('matric_number')
    selected_station_id = request.GET.get('station_id')
    
    selected_candidate = None
    selected_station = None
    activities_data = []

    candidates = Candidate.objects.all()
    
    if selected_matric:
        selected_candidate = get_object_or_404(Candidate, matric_number=selected_matric)
        stations = selected_candidate.procedure_stations.all()

        # Only assign default station if candidate has stations
        if selected_station_id:
            selected_station = get_object_or_404(ProcedureStation, id=selected_station_id)
        elif stations.exists():
            selected_station = stations.first()

        if selected_station:
            for activity in selected_station.activities.all():
                score_obj = Score.objects.filter(candidate=selected_candidate, activity=activity).first()
                options = activity.get_score_options()
                activities_data.append({
                    'activity_id': activity.id,
                    'description': activity.description,
                    'max_score': activity.max_score,
                    'score': score_obj.score if score_obj else None,
                    'options': options
                })

    context = {
        'candidates': candidates,
        'selected_candidate': selected_candidate,
        'stations': selected_candidate.procedure_stations.all() if selected_candidate else [],
        'selected_station': selected_station,
        'activities': activities_data
    }
    return render(request, 'base/home.html', context)





# @csrf_exempt
# def save_scores(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        matric_number = data.get('matric_number')
        score_entries = data.get('scores', [])

        candidate = Candidate.objects.get(matric_number=matric_number)

        for entry in score_entries:
            activity_id = entry['activity_id']
            score_val = entry['score']

            activity = Activity.objects.get(id=activity_id)

            Score.objects.update_or_create(
                candidate=candidate,
                activity=activity,
                defaults={'score': score_val}
            )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def save_scores(request):
    if request.method == 'POST':
        matric_number = request.POST.get('matric_number')
        station_id = request.POST.get('station_id')

        candidate = get_object_or_404(Candidate, matric_number=matric_number)

        for key, value in request.POST.items():
            if key.startswith('score_'):
                activity_id = key.split('_')[1]
                try:
                    activity = Activity.objects.get(id=activity_id)
                    score_val = float(value)

                    Score.objects.update_or_create(
                        candidate=candidate,
                        activity=activity,
                        defaults={'score': score_val}
                    )
                except (Activity.DoesNotExist, ValueError):
                    continue

        return redirect(f'?matric_number={matric_number}&station_id={station_id}')

    return redirect('base/dashboard')
