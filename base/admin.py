from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe


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


class LevelListFilter(admin.SimpleListFilter):
    """Custom filter for level choices"""
    title = 'Level'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return ProcedureStation.LEVEL_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(level=self.value())
        return queryset

class ProcedureStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_level_display', 'session', 'description_short')
    list_filter = (LevelListFilter, 'session')  # Add session filter too
    search_fields = ('name', 'description')
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

    def get_level_display(self, obj):
        return dict(ProcedureStation.LEVEL_CHOICES).get(obj.level, 'All Levels')
    get_level_display.short_description = 'Level'

class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'truncated_description', 
        'station_name',
        'session_name',
        'level_display',
        'max_score',
        'score_options'
    )
    list_filter = (
        ('station__level', admin.ChoicesFieldListFilter),
        'station__session',
        'station'
    )
    search_fields = (
        'description',
        'station__name',
        'station__session__name'
    )
    raw_id_fields = ('station',)
    
    def truncated_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    truncated_description.short_description = 'Description'
    
    def station_name(self, obj):
        return obj.station.name
    station_name.short_description = 'Station'
    station_name.admin_order_field = 'station__name'
    
    def session_name(self, obj):
        return obj.station.session.name
    session_name.short_description = 'Session'
    session_name.admin_order_field = 'station__session__name'
    
    def level_display(self, obj):
        return obj.station.get_level_display()
    level_display.short_description = 'Level'
    level_display.admin_order_field = 'station__level'
    
    def score_options(self, obj):
        return ", ".join(map(str, obj.get_score_options()))
    score_options.short_description = 'Scoring Options'


class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'matric_number',
        'level_display',
        'session',
        'passport_preview'
    )
    list_filter = (
        'level',
        'session',
    )
    search_fields = (
        'full_name',
        'matric_number',
        'session__name'
    )
    list_select_related = ('session',)
    readonly_fields = ('passport_preview',)
    
    def level_display(self, obj):
        return obj.get_level_display()
    level_display.short_description = 'Level'
    level_display.admin_order_field = 'level'
    
    def passport_preview(self, obj):
        if obj.passport:
            return mark_safe(f'<img src="{obj.passport.url}" width="50" height="50" />')
        return "No Image"
    passport_preview.short_description = 'Passport'
    
    # Optional: Group fields in the edit view
    fieldsets = (
        (None, {
            'fields': ('matric_number', 'full_name', 'level', 'session')
        }),
        ('Passport Photo', {
            'fields': ('passport', 'passport_preview'),
            'classes': ('collapse',)
        }),
    )



# Register your models here.

admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(Session)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(ProcedureStation, ProcedureStationAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Score)
admin.site.register(VivaScore)
