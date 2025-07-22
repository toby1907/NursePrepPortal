from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Session(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    matric_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    passport = models.ImageField(upload_to='passports/', null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return f"{self.full_name} ({self.matric_number})"


class ProcedureStation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='procedure_stations')
    candidates = models.ManyToManyField(Candidate, related_name='procedure_stations')

    def __str__(self):
        return f"{self.name} - {self.session.name}"


class Activity(models.Model):
    station = models.ForeignKey(ProcedureStation, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField()
    max_score = models.FloatField()

    def __str__(self):
        return f"{self.description[:30]}... ({self.station.name})"

    def get_score_options(self):
        sc = self.max_score / 4
        return [round(sc * i, 2) for i in range(5)]


class Score(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    score = models.FloatField()
    
    class Meta:
        unique_together = ('candidate', 'activity')

    def __str__(self):
        return f"{self.candidate} - {self.activity} - {self.score}"


class VivaScore(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"{self.candidate} - Viva: {self.score}"


class FinalGrade(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE)
    viva = models.FloatField()
    total = models.FloatField(blank=True, null=True)

    def calculate_total(self):
        activity_total = Score.objects.filter(candidate=self.candidate).aggregate(models.Sum('score'))['score__sum'] or 0
        return activity_total + self.viva

    def save(self, *args, **kwargs):
        self.total = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate} - Total Grade: {self.total}"
