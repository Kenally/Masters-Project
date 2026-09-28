import joblib
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import CONSTRUCT_ITEMS, AssessmentForm
from .models import Assessment, Rule

_model_cache = None


def get_model():
    """Load the trained CART model once and cache it for the process lifetime."""
    global _model_cache
    if _model_cache is None:
        if not settings.ML_MODEL_PATH.exists():
            return None
        _model_cache = joblib.load(settings.ML_MODEL_PATH)
    return _model_cache


def home(request):
    return render(request, "assessment/home.html", {
        "model_ready": get_model() is not None,
        "recent_assessments": Assessment.objects.all()[:5],
    })


def assessment_form(request):
    bundle = get_model()
    if bundle is None:
        messages.error(
            request,
            "No trained model found yet. Run analysis/analyze_and_train.py first, "
            "then restart the server."
        )
        return redirect("home")

    if request.method == "POST":
        form = AssessmentForm(request.POST)
        if form.is_valid():
            scores = form.construct_scores()
            features = bundle["features"]
            X = pd.DataFrame([[scores[f] for f in features]], columns=features)
            predicted_level = bundle["model"].predict(X)[0]

            assessment = Assessment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                institution_name=form.cleaned_data["institution_name"],
                institution_type=form.cleaned_data["institution_type"],
                transparency_score=scores["transparency"],
                accountability_score=scores["accountability"],
                fairness_score=scores["fairness"],
                data_protection_score=scores["data_protection"],
                liability_score=scores["liability"],
                oversight_score=scores["oversight"],
                predicted_adoption_level=predicted_level,
            )
            return redirect("assessment_result", pk=assessment.pk)
    else:
        form = AssessmentForm()

    # Group fields by construct for the template
    grouped_fields = []
    for construct, data in CONSTRUCT_ITEMS.items():
        fields = [form[f"{construct}_{i}"] for i in range(1, len(data["items"]) + 1)]
        grouped_fields.append({"label": data["label"], "fields": fields})

    return render(request, "assessment/assessment_form.html", {
        "form": form,
        "grouped_fields": grouped_fields,
    })


def assessment_result(request, pk):
    assessment = Assessment.objects.get(pk=pk)

    # Surface a few rules relevant to this respondent's predicted level, if any exist
    relevant_rules = Rule.objects.filter(
        consequents__icontains=assessment.predicted_adoption_level
    )[:5]

    return render(request, "assessment/assessment_result.html", {
        "assessment": assessment,
        "relevant_rules": relevant_rules,
    })


def rules_list(request):
    rules = Rule.objects.all()
    return render(request, "assessment/rules_list.html", {"rules": rules})
