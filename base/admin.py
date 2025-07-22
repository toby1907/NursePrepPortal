from django.contrib import admin


from .models import (
    Session,
    Candidate,
    ProcedureStation,
    Activity,
    Score,
    VivaScore,
    FinalGrade
)


# Register your models here.


admin.site.register(Session)
admin.site.register(Candidate)
admin.site.register(ProcedureStation)
admin.site.register(Activity)
admin.site.register(Score)
admin.site.register(VivaScore)
