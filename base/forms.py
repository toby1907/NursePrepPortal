from django import forms
from .models import GlobalSettings, Session, Candidate

class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = GlobalSettings
        fields = ['active_session', 'active_level']
        widgets = {
            'active_session': forms.Select(attrs={'class': 'form-control'}),
            'active_level': forms.Select(attrs={'class': 'form-control'}),
        }



class BatchUploadForm(forms.Form):
    UPLOAD_TYPE_CHOICES = [
        ('candidates', 'Candidates'),
        ('stations', 'Stations'),
        ('activities', 'Activities'),
        ('combined', 'Stations with Activities')
    ]
    
    upload_type = forms.ChoiceField(choices=UPLOAD_TYPE_CHOICES)
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        required=True
    )
    level = forms.TypedChoiceField(
        choices=[('', 'All Levels')] + Candidate.LEVEL_CHOICES,
        coerce=int,
        required=False,
        help_text="Only required for stations/candidates"
    )
    csv_file = forms.FileField(label='CSV File')