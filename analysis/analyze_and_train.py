"""
AI Ethics and Regulatory Readiness Survey - Analysis and Model Training
=========================================================================
See README.md for full usage instructions.
"""

import json
import re
import sys
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

HERE = Path(__file__).resolve().parent
RESPONSES_PATH = HERE / "responses.csv"
OUTPUT_DIR = HERE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

DJANGO_ML_DIR = HERE.parent / "django_app" / "assessment" / "ml"
DJANGO_ML_DIR.mkdir(parents=True, exist_ok=True)

CONSTRUCTS = {
    "transparency": [
        "publishes documentation explaining how ai systems make decisions",
        "customers can request explanations",
        "ai models are documented with clear input and output",
        "transparency reports on ai system performance",
        "external auditors can access our ai model documentation",
    ],
    "accountability": [
        "designated personnel responsible for ai ethics",
        "clear escalation paths when ai systems produce errors",
        "board-level committees review ai deployment",
        "maintain audit trails for all ai-driven decisions",
        "responsibility for ai outcomes is clearly assigned",
    ],
    "fairness": [
        "test our ai systems for demographic bias",
        "training data is representative of the populations",
        "monitor ai outcomes for disparities",
        "fairness metrics are included in our ai performance",
        "procedures to correct biased ai outcomes",
    ],
    "data_protection": [
        "comply with the nigeria data protection act",
        "customer consent is obtained before data is used",
        "privacy impact assessments before deploying ai",
        "encrypt personal data used by ai systems",
        "data retention policies for ai training data",
    ],
    "liability": [
        "contracts with ai vendors clearly assign liability",
        "carry insurance covering ai-related operational risks",
        "terms of service explain liability for ai-driven",
        "legal counsel reviews ai deployment plans",
        "understand our liability position under nigerian law",
    ],
    "oversight": [
        "regulators have sufficient technical expertise",
        "regulatory examinations include ai-specific review",
        "clear reporting requirements for ai incidents",
        "inter-agency coordination exists for ai oversight",
        "regulatory sandboxes or safe harbours",
    ],
    "adoption": [
        "deployed ai in multiple business processes",
        "dedicated budget for ai development and procurement",
        "ai systems are integrated with our core banking",
        "staff across our institution have received training",
        "management has committed to expanding ai use",
    ],
}

PREDICTOR_CONSTRUCTS = ["transparency", "accountability", "fairness", "data_protection", "liability", "oversight"]
TARGET_CONSTRUCT = "adoption"


def normalise(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def find_column(df_columns, keyword):
    for col in df_columns:
        if keyword in normalise(col):
            return col
    return None


def extract_score(value):
    if pd.isna(value):
        return np.nan
    match = re.match(r"\s*([1-5])", str(value))
    return int(match.group(1)) if match else np.nan


def cronbach_alpha(item_df):
    item_df = item_df.dropna()
    k = item_df.shape[1]
    if k < 2 or item_df.shape[0] < 2:
        return np.nan
    item_variances = item_df.var(axis=0, ddof=1)
    total_variance = item_df.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_variances.sum() / total_variance)


def main():
    if not RESPONSES_PATH.exists():
        sys.exit(f"Could not find {RESPONSES_PATH}.")

    raw = pd.read_csv(RESPONSES_PATH)
    print(f"Loaded {len(raw)} responses with {len(raw.columns)} columns.\n")

    construct_item_cols = {}
    scored = pd.DataFrame(index=raw.index)

    for construct, keywords in CONSTRUCTS.items():
        cols = []
        for i, kw in enumerate(keywords, start=1):
            col = find_column(raw.columns, kw)
            if col is None:
                print(f"WARNING: could not find a column for {construct} item {i} "
                      f"(keyword: '{kw}'). This item will be skipped.")
                continue
            score_col = f"{construct}_{i}"
            scored[score_col] = raw[col].apply(extract_score)
            cols.append(score_col)
        construct_item_cols[construct] = cols

    for construct, cols in construct_item_cols.items():
        if cols:
            scored[construct] = scored[cols].mean(axis=1)
        else:
            scored[construct] = np.nan

    print("Cronbach's alpha (internal consistency) per construct:")
    alpha_report = {}
    for construct, cols in construct_item_cols.items():
        if len(cols) >= 2:
            alpha = cronbach_alpha(scored[cols])
            alpha_report[construct] = round(alpha, 3)
            print(f"  {construct:16s} alpha = {alpha:.3f}  (n items = {len(cols)})")
        else:
            print(f"  {construct:16s} skipped (fewer than 2 matched items)")
    print()

    scored = scored.dropna(subset=PREDICTOR_CONSTRUCTS + [TARGET_CONSTRUCT])
    if len(scored) < 15:
        print(f"WARNING: only {len(scored)} complete responses available. "
              "The model below will be trained, but treat results with caution "
              "until more responses come in.")

    # Fixed thresholds per thesis methodology 3.3.1 (NOT tertiles):
    # Low 1.00-2.33, Moderate 2.34-3.66, High 3.67-5.00
    def bucket(x):
        if x <= 2.33:
            return "Low"
        elif x <= 3.66:
            return "Moderate"
        return "High"
    scored["adoption_level"] = scored[TARGET_CONSTRUCT].apply(bucket)

    print("AI Adoption Level distribution:")
    print(scored["adoption_level"].value_counts(), "\n")

    constructs_csv = OUTPUT_DIR / "constructs.csv"
    scored.to_csv(constructs_csv, index=False)
    print(f"Saved cleaned construct scores to {constructs_csv}\n")

    X = scored[PREDICTOR_CONSTRUCTS]
    y = scored["adoption_level"]

    smallest_group = y.value_counts().min()
    n_folds = min(10, smallest_group) if smallest_group >= 2 else 2
    if n_folds < 10:
        print(f"NOTE: using {n_folds}-fold cross-validation instead of 10-fold, "
              "because the smallest adoption-level group has fewer than 10 respondents.\n")

    tree = DecisionTreeClassifier(criterion="entropy", max_depth=5, random_state=42)
    cv_scores = cross_val_score(tree, X, y, cv=n_folds)
    print(f"Decision tree cross-validation accuracy: "
          f"{cv_scores.mean():.3f} (+/- {cv_scores.std():.3f}) across {n_folds} folds")

    tree.fit(X, y)
    print("\nDecision tree rules:")
    print(export_text(tree, feature_names=PREDICTOR_CONSTRUCTS))

    plt.figure(figsize=(16, 9))
    plot_tree(tree, feature_names=PREDICTOR_CONSTRUCTS, class_names=tree.classes_,
              filled=True, rounded=True, fontsize=9)
    tree_png = OUTPUT_DIR / "decision_tree.png"
    plt.savefig(tree_png, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved decision tree diagram to {tree_png}")

    model_path = DJANGO_ML_DIR / "model.pkl"
    joblib.dump(
        {"model": tree, "features": PREDICTOR_CONSTRUCTS, "classes": list(tree.classes_)},
        model_path,
    )
    print(f"Saved trained model for the Django app to {model_path}\n")

    binarised = pd.DataFrame(index=scored.index)
    for construct in PREDICTOR_CONSTRUCTS + [TARGET_CONSTRUCT]:
        median = scored[construct].median()
        binarised[f"{construct}_High"] = scored[construct] >= median
        binarised[f"{construct}_Low"] = scored[construct] < median

    frequent_itemsets = apriori(binarised, min_support=0.15, use_colnames=True, max_len=3)
    if frequent_itemsets.empty:
        print("No frequent itemsets found at 15% minimum support; try lowering "
              "min_support once more responses come in.")
        rules = pd.DataFrame()
    else:
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
        rules = rules[
            rules["consequents"].apply(lambda s: len(s) == 1 and next(iter(s)).startswith("adoption_"))
        ]
        rules = rules.sort_values(["lift", "confidence"], ascending=False).head(20)

    print(f"Found {len(rules)} association rules (adoption-focused, >=15% support, >=70% confidence, top 20 by lift).\n")

    rules_records = []
    for _, r in rules.iterrows():
        rules_records.append({
            "antecedents": ", ".join(sorted(r["antecedents"])),
            "consequents": ", ".join(sorted(r["consequents"])),
            "support": round(r["support"], 3),
            "confidence": round(r["confidence"], 3),
            "lift": round(r["lift"], 3),
        })

    rules_json_path = DJANGO_ML_DIR / "rules.json"
    with open(rules_json_path, "w") as f:
        json.dump(rules_records, f, indent=2)
    print(f"Saved association rules to {rules_json_path}")

    rules_csv_path = OUTPUT_DIR / "association_rules.csv"
    pd.DataFrame(rules_records).to_csv(rules_csv_path, index=False)
    print(f"Saved association rules to {rules_csv_path}\n")

    with open(OUTPUT_DIR / "reliability_report.json", "w") as f:
        json.dump(alpha_report, f, indent=2)

    print("Done. Next: cd ../django_app && python manage.py migrate "
          "&& python manage.py load_rules && python manage.py runserver")


if __name__ == "__main__":
    main()
