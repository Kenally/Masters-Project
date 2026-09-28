from django import forms

SCALE_CHOICES = [
    (1, "1 - Strongly Disagree"),
    (2, "2 - Disagree"),
    (3, "3 - Neutral"),
    (4, "4 - Agree"),
    (5, "5 - Strongly Agree"),
]

# Six predictor constructs and their five items each, matching the survey.
# (AI Adoption Level itself is not asked here, it's what the model predicts.)
CONSTRUCT_ITEMS = {
    "transparency": {
        "label": "Transparency",
        "items": [
            "Our institution publishes documentation explaining how AI systems make decisions.",
            "Customers can request explanations for AI-driven financial decisions.",
            "Our AI models are documented with clear input and output specifications.",
            "We provide transparency reports on AI system performance.",
            "External auditors can access our AI model documentation.",
        ],
    },
    "accountability": {
        "label": "Accountability",
        "items": [
            "Our institution has designated personnel responsible for AI ethics.",
            "There are clear escalation paths when AI systems produce errors.",
            "Board-level committees review AI deployment decisions.",
            "We maintain audit trails for all AI-driven decisions.",
            "Responsibility for AI outcomes is clearly assigned in our organisation.",
        ],
    },
    "fairness": {
        "label": "Fairness",
        "items": [
            "We test our AI systems for demographic bias before deployment.",
            "Our training data is representative of the populations we serve.",
            "We monitor AI outcomes for disparities across gender and geography.",
            "Fairness metrics are included in our AI performance dashboards.",
            "We have procedures to correct biased AI outcomes when detected.",
        ],
    },
    "data_protection": {
        "label": "Data Protection",
        "items": [
            "Our AI systems comply with the Nigeria Data Protection Act 2023.",
            "Customer consent is obtained before data is used for AI training.",
            "We conduct privacy impact assessments before deploying AI systems.",
            "We encrypt personal data used by AI systems.",
            "Data retention policies for AI training data are clearly defined.",
        ],
    },
    "liability": {
        "label": "Liability Mechanisms",
        "items": [
            "Our contracts with AI vendors clearly assign liability for system errors.",
            "We carry insurance covering AI-related operational risks.",
            "Our terms of service explain liability for AI-driven decisions.",
            "Legal counsel reviews AI deployment plans for liability exposure.",
            "We understand our liability position under Nigerian law for AI harms.",
        ],
    },
    "oversight": {
        "label": "Oversight Capacity",
        "items": [
            "Our regulators have sufficient technical expertise to evaluate AI systems.",
            "Regulatory examinations include AI-specific review procedures.",
            "There are clear reporting requirements for AI incidents to regulators.",
            "Inter-agency coordination exists for AI oversight in finance.",
            "Regulatory sandboxes or safe harbours are available for AI testing.",
        ],
    },
}

INSTITUTION_TYPE_CHOICES = [
    ("Commercial Bank", "Commercial Bank"),
    ("Fintech", "Fintech"),
    ("Insurance", "Insurance"),
    ("Microfinance", "Microfinance"),
]


class AssessmentForm(forms.Form):
    institution_name = forms.CharField(max_length=255, required=False, label="Institution name (optional)")
    institution_type = forms.ChoiceField(choices=INSTITUTION_TYPE_CHOICES, label="Institution type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for construct, data in CONSTRUCT_ITEMS.items():
            for i, item_text in enumerate(data["items"], start=1):
                field_name = f"{construct}_{i}"
                self.fields[field_name] = forms.TypedChoiceField(
                    choices=SCALE_CHOICES,
                    coerce=int,
                    widget=forms.RadioSelect,
                    label=item_text,
                )

    def construct_scores(self):
        """Return {construct_name: mean_score} using this form's cleaned_data."""
        scores = {}
        for construct, data in CONSTRUCT_ITEMS.items():
            values = [self.cleaned_data[f"{construct}_{i}"] for i in range(1, len(data["items"]) + 1)]
            scores[construct] = sum(values) / len(values)
        return scores
