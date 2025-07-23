
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Candidate, Score, ProcedureStation, Activity, Session,VivaScore, FinalGrade
from django.db.models import Prefetch, Sum
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.forms import modelform_factory
from django.db import transaction
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('dashboard')
      
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password') 

        try:
            user = User.objects.get(username= username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Userername OR password does not exist')

        

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('dashboard')

def registerPage(request):
    form = UserCreationForm()
    page = 'register'
   
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})

@login_required(login_url='login')
def dashboard(request):
    selected_matric = request.GET.get('matric_number')
    selected_station_id = request.GET.get('station_id')

    selected_candidate = None
    selected_station = None
    activities_data = []

    candidates = Candidate.objects.all()
    stations = ProcedureStation.objects.all()

    if selected_station_id:
        selected_station = get_object_or_404(ProcedureStation, id=selected_station_id)

        # If candidate is selected, show scores
        if selected_matric:
            selected_candidate = get_object_or_404(Candidate, matric_number=selected_matric)

            if not selected_station and selected_candidate.procedure_stations.exists():
                selected_station = selected_candidate.procedure_stations.first()

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
        else:
            # Candidate not selected: show activities without scores
            for activity in selected_station.activities.all():
                activities_data.append({
                    'activity_id': activity.id,
                    'description': activity.description,
                    'max_score': activity.max_score,
                    'score': None,
                    'options': activity.get_score_options()
                })

    context = {
        'candidates': candidates,
        'selected_candidate': selected_candidate,
        'stations': stations,
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


@login_required(login_url='login')
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

        # ✅ Correct redirect with reverse and query string
        
        messages.success(request, f'Scores saved successfully for {matric_number}.')

        dashboard_url = reverse('dashboard')
        return redirect(f'{dashboard_url}?matric_number={matric_number}&station_id={station_id}')

    # Optional fallback
    messages.success(request, f'Scores saved successfully for {matric_number}.')
    return redirect(reverse('dashboard'))



@login_required(login_url='login')
def viva_scoring_view(request):
    current_session = Session.objects.latest('start_date')
    candidates = Candidate.objects.filter(session=current_session)

    if request.method == 'POST':
        with transaction.atomic():
            for candidate in candidates:
                score_value = request.POST.get(f'score_{candidate.id}')
                if score_value:
                    score_value = float(score_value)
                    if 0 <= score_value <= 10:
                        VivaScore.objects.update_or_create(
                            candidate=candidate,
                            defaults={'score': score_value}
                        )
        messages.success(request, f'Scores saved successfully.')
        return redirect('viva_scores')  # or a success page
   
    return render(request, 'base/viva.html', {'candidates': candidates})



@login_required(login_url='login')
def final_grade_report(request):
    current_session = Session.objects.latest('start_date')
    candidates = Candidate.objects.filter(session=current_session)
    stations = ProcedureStation.objects.filter(session=current_session)

    report_data = []

    for candidate in candidates:
    # Get or create VivaScore
        viva_score = VivaScore.objects.filter(candidate=candidate).first()
        viva = viva_score.score if viva_score else 0

        # Get or create FinalGrade
        final_grade, created = FinalGrade.objects.get_or_create(candidate=candidate, defaults={'viva': viva})
        if not created:
            final_grade.viva = viva
        final_grade.save()  # This triggers calculate_total()

        # Station scores
        station_scores = []
        for station in stations:
            total_score = Score.objects.filter(
                candidate=candidate,
                activity__station=station
            ).aggregate(Sum('score'))['score__sum'] or 0
            station_scores.append((station.name, total_score))

        report_data.append({
            'matric_number': candidate.matric_number,
            'full_name': candidate.full_name,
            'station_scores': station_scores,
            'viva': viva,
            'total': final_grade.total
        })


    return render(request, 'base/final_grade_report.html', {'report_data': report_data,'stations': stations })


@login_required(login_url='login')
@require_POST
def recalculate_grades(request):
    current_session = Session.objects.latest('start_date')
    candidates = Candidate.objects.filter(session=current_session)

    for candidate in candidates:
        viva_score = VivaScore.objects.filter(candidate=candidate).first()
        viva = viva_score.score if viva_score else 0

        final_grade, _ = FinalGrade.objects.get_or_create(candidate=candidate)
        final_grade.viva = viva
        final_grade.save()  # Triggers total recalculation

    messages.success(request, "Grades recalculated successfully.")
    return redirect('final_grade_report')





@login_required(login_url='login')
def download_grade_report_pdf(request):
    current_session = Session.objects.latest('start_date')
    candidates = Candidate.objects.filter(session=current_session)
    stations = ProcedureStation.objects.filter(session=current_session)

    report_data = []
    for candidate in candidates:
        viva_score = VivaScore.objects.filter(candidate=candidate).first()
        viva = viva_score.score if viva_score else 0
        final_grade = FinalGrade.objects.get(candidate=candidate)
        station_scores = []
        for station in stations:
            total_score = Score.objects.filter(
                candidate=candidate,
                activity__station=station
            ).aggregate(Sum('score'))['score__sum'] or 0
            station_scores.append((station.name, total_score))

        report_data.append({
            'matric_number': candidate.matric_number,
            'full_name': candidate.full_name,
            'station_scores': station_scores,
            'viva': viva,
            'total': final_grade.total
        })

    template = get_template('base/final_grade_report_pdf.html')
    html = template.render({'report_data': report_data, 'stations': stations})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="final_grade_report.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
