from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        settings = GlobalSettings.objects.first()
        
        if settings and settings.active_session:
            qs = qs.filter(session=settings.active_session)
        
        if settings and settings.active_level:
            if self.model.__name__ == 'ProcedureStation':
                qs = qs.filter(models.Q(level=settings.active_level) | models.Q(level__isnull=True))
            elif self.model.__name__ == 'Candidate':
                qs = qs.filter(level=settings.active_level)
        
        return qs
    
class Session(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
   

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")

    def __str__(self):
        return self.name


class Candidate(models.Model):
    LEVEL_CHOICES = [
        (100, '100 Level'),
        (200, '200 Level'),
        (300, '300 Level'),
        (400, '400 Level'),
        (500, '500 Level'),
        (600, '600 Level'),
    ]
    level = models.PositiveSmallIntegerField(
        choices=LEVEL_CHOICES,
        default=100,  # Sets default to 100 Level
        validators=[MinValueValidator(100), MaxValueValidator(600)]
    ) 
    matric_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    passport = models.ImageField(upload_to='passports/', null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='candidates')
    objects = models.Manager()  # default manager
    active = ActiveManager()    # custom manager

    def __str__(self):
        return f"{self.full_name} ({self.matric_number})"


class ProcedureStation(models.Model):
    class Meta:
        unique_together = [['name', 'level', 'session']]
    LEVEL_CHOICES = [
        (None, 'All Levels'),  # None means station is for all levels
        (100, '100 Level'),
        (200, '200 Level'),
        (300, '300 Level'),
        (400, '400 Level'),
        (500, '500 Level'),
        (600, '600 Level'),
        # ... keep same levels as above ...
    ]
    level = models.PositiveSmallIntegerField(
        choices=LEVEL_CHOICES,
        null=True,  # Makes it optional
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(600)])
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='procedure_stations')
    candidates = models.ManyToManyField(Candidate, related_name='procedure_stations')
    objects = models.Manager()  # default manager
    active = ActiveManager()    # custom manager

    def __str__(self):
        return f"{self.name} - {self.session.name}"


class Activity(models.Model):
    station = models.ForeignKey(ProcedureStation, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField()
    max_score = models.FloatField()

    @property
    def level(self):
        return self.station.level

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

    
    def clean(self):
        if self.score < 0 or self.score > 10:
            raise ValidationError("Viva score must be between 0 and 10.")


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

class GlobalSettings(models.Model):
    active_session = models.ForeignKey('Session', on_delete=models.SET_NULL, null=True, blank=True)
    active_level = models.PositiveSmallIntegerField(
        choices=Candidate.LEVEL_CHOICES, 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return f"Current Settings (Session: {self.active_session}, Level: {self.get_active_level_display()})"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)
