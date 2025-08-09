from django import forms
from .models import GlobalSettings, Session

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
    ]
    
    upload_type = forms.ChoiceField(choices=UPLOAD_TYPE_CHOICES)
    session = forms.ModelChoiceField(queryset=Session.objects.all())
    csv_file = forms.FileField(label='CSV File')