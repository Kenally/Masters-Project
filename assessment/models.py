from django.conf import settings
from django.db import models


class Assessment(models.Model):
    """One completed AI ethics/regulatory readiness assessment for an institution."""

    ADOPTION_LEVEL_CHOICES = [
        ("Low", "Low"),
        ("Moderate", "Moderate"),
        ("High", "High"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assessments",
    )
    institution_name = models.CharField(max_length=255, blank=True)
    institution_type = models.CharField(max_length=50, blank=True)

    transparency_score = models.FloatField()
    accountability_score = models.FloatField()
    fairness_score = models.FloatField()
    data_protection_score = models.FloatField()
    liability_score = models.FloatField()
    oversight_score = models.FloatField()

    predicted_adoption_level = models.CharField(max_length=10, choices=ADOPTION_LEVEL_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.institution_name or f"Assessment #{self.pk}"
        return f"{label} — {self.predicted_adoption_level}"


class Rule(models.Model):
    """One association rule discovered by the Apriori step in analyze_and_train.py."""

    antecedents = models.CharField(max_length=500)
    consequents = models.CharField(max_length=500)
    support = models.FloatField()
    confidence = models.FloatField()
    lift = models.FloatField()

    class Meta:
        ordering = ["-confidence", "-lift"]

    def __str__(self):
        return f"{self.antecedents} -> {self.consequents}"
