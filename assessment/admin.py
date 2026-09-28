from django.contrib import admin

from .models import Assessment, Rule


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("institution_name", "institution_type", "predicted_adoption_level", "created_at")
    list_filter = ("institution_type", "predicted_adoption_level")


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("antecedents", "consequents", "support", "confidence", "lift")
    ordering = ("-confidence", "-lift")
