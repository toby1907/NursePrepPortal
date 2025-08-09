from django.contrib import admin
from django import forms



from .models import (
    Session,
    Candidate,
    ProcedureStation,
    Activity,
    Score,
    VivaScore,
    FinalGrade,
    GlobalSettings
)


class GlobalSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow only one settings instance
        return not GlobalSettings.objects.exists()



# Register your models here.

admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(Session)
admin.site.register(Candidate)
admin.site.register(ProcedureStation)
admin.site.register(Activity)
admin.site.register(Score)
admin.site.register(VivaScore)
