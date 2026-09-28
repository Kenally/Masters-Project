from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("assess/", views.assessment_form, name="assessment_form"),
    path("assess/result/<int:pk>/", views.assessment_result, name="assessment_result"),
    path("rules/", views.rules_list, name="rules_list"),
]
