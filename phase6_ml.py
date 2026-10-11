from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


MAX_INPUT_BYTES = 500 * 1024 * 1024
NUMERIC_FEATURES = ["bytes", "hour_utc", "day_of_week"]
CATEGORICAL_FEATURES = ["source", "action"]
REQUIRED_COLUMNS = {
    "event_id",
    "timestamp",
    "source",
    "action",
    "bytes",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(4 * 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def load_events(
    csv_path_text: str,
    group_column: str,
    label_column: str | None,
) -> tuple[pd.DataFrame, Path]:
    path = Path(csv_path_text).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"CSV input is not a regular file: {path}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"CSV exceeds {MAX_INPUT_BYTES} bytes.")

    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    df.columns = [str(column).strip() for column in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if group_column not in df.columns:
        raise ValueError(
            f"Group column {group_column!r} is missing. "
            "Use a scenario/case grouping column to prevent row-level leakage."
        )

    if label_column and label_column not in df.columns:
        raise ValueError(f"Label column {label_column!r} is missing.")

    if df.empty:
        raise ValueError("CSV has no event rows.")

    # Require ISO timestamps with an explicit timezone. Do not silently treat
    # naive device times as UTC.
    parsed_times = []
    for row_number, raw in enumerate(df["timestamp"], start=2):
        try:
            value = str(raw).strip()
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timezone is absent")
            parsed_times.append(parsed.astimezone(timezone.utc))
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(
                f"Invalid timestamp at CSV row {row_number}; "
                "use ISO-8601 with an explicit timezone, e.g. 2026-10-01T09:00:00Z."
            ) from exc

    times = pd.to_datetime(parsed_times, utc=True)
    df["hour_utc"] = times.hour + times.minute / 60.0
    df["day_of_week"] = times.dayofweek

    df["bytes"] = pd.to_numeric(df["bytes"], errors="coerce")
    if df["bytes"].isna().any() or (df["bytes"] < 0).any():
        raise ValueError("bytes must contain non-negative numeric values.")

    for column in ("source", "action", group_column, "event_id"):
        df[column] = df[column].fillna("").astype(str).str.strip()
        if (df[column] == "").any():
            raise ValueError(f"Column {column!r} cannot contain blank values.")

    df["source"] = df["source"].replace("", "(missing)")
    df["action"] = df["action"].replace("", "(missing)")

    if label_column:
        labels = pd.to_numeric(df[label_column], errors="coerce")
        if labels.isna().any() or not set(labels.unique()).issubset({0, 1}):
            raise ValueError(
                f"{label_column!r} must contain only integer labels 0 and 1."
            )
        df[label_column] = labels.astype(int)
        if set(df[label_column].unique()) != {0, 1}:
            raise ValueError("Training data must contain both label classes 0 and 1.")

    return df, path


def make_pipeline() -> Pipeline:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    classifier = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def choose_group_holdout(
    x: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
):
    unique_groups = groups.nunique()
    if unique_groups < 4:
        raise ValueError(
            "Need at least four distinct groups for a grouped holdout. "
            "A group should represent a case, scenario, or other unit that "
            "must not be split across training and test."
        )

    splitter = GroupShuffleSplit(
        n_splits=100,
        test_size=0.25,
        random_state=42,
    )

    for train_index, test_index in splitter.split(x, y, groups):
        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]
        if y_train.nunique() == 2 and y_test.nunique() == 2:
            train_groups = set(groups.iloc[train_index])
            test_groups = set(groups.iloc[test_index])
            if train_groups.isdisjoint(test_groups):
                return train_index, test_index

    raise ValueError(
        "Could not find a group-separated split with both classes in both "
        "sets. Add more independently labeled groups; do not fall back to "
        "random row splitting."
    )


def create_run_dir(root_text: str) -> Path:
    root = Path(root_text).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    output = root / (
        f"train-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    )
    output.mkdir(parents=False, exist_ok=False)
    return output


def train(args) -> int:
    df, csv_path = load_events(args.input, args.group_column, args.label_column)
    y = df[args.label_column].astype(int)

    # IDs and grouping columns are intentionally excluded from model features.
    x = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    groups = df[args.group_column]

    train_idx, test_idx = choose_group_holdout(x, y, groups)
    x_train, x_test = x.iloc[train_idx], x.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    model = make_pipeline()
    model.fit(x_train, y_train)

    predicted = model.predict(x_test).astype(int)
    class_positions = list(model.named_steps["classifier"].classes_)
    if 1 not in class_positions:
        raise ValueError("Trained classifier does not contain positive class 1.")
    positive_index = class_positions.index(1)
    positive_scores = model.predict_proba(x_test)[:, positive_index]

    metrics = {
        "schema": "chronofact-phase6-evaluation-v1",
        "created_at_utc": utc_now(),
        "dataset_path": str(csv_path),
        "dataset_sha256": sha256_file(csv_path),
        "target_column": args.label_column,
        "group_column": args.group_column,
        "rows_total": int(len(df)),
        "rows_train": int(len(train_idx)),
        "rows_test": int(len(test_idx)),
        "groups_total": int(groups.nunique()),
        "groups_train": int(groups.iloc[train_idx].nunique()),
        "groups_test": int(groups.iloc[test_idx].nunique()),
        "train_groups_disjoint_from_test": set(groups.iloc[train_idx]).isdisjoint(
            set(groups.iloc[test_idx])
        ),
        "positive_label_definition": args.positive_label_definition,
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "threshold_for_reported_predictions": 0.5,
        "precision": float(
            precision_score(y_test, predicted, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predicted, zero_division=0)
        ),
        "average_precision": float(
            average_precision_score(y_test, positive_scores)
        ),
        "confusion_matrix_labels_0_then_1": confusion_matrix(
            y_test, predicted, labels=[0, 1]
        ).tolist(),
        "classification_report": classification_report(
            y_test,
            predicted,
            labels=[0, 1],
            target_names=["label_0", "label_1"],
            zero_division=0,
            output_dict=True,
        ),
        "positive_score_note": (
            "The Random Forest positive-class score is not calibrated and is "
            "not a probability of wrongdoing or evidence credibility."
        ),
        "limitations": [
            "One group-separated holdout is not independent external validation.",
            "Synthetic dataset performance does not establish real-world accuracy.",
            "Model flags are review leads only, not evidence of guilt.",
        ],
    }

    # ROC-AUC is included only when both labels are present in the test set.
    if y_test.nunique() == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_test, positive_scores))

    output_dir = create_run_dir(args.output_root)
    model_path = output_dir / "model.joblib"
    metadata = {
        "schema": "chronofact-phase6-model-v1",
        "created_at_utc": utc_now(),
        "model_type": "RandomForestClassifier",
        "target_column": args.label_column,
        "group_column": args.group_column,
        "feature_columns": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "positive_label_definition": args.positive_label_definition,
        "dataset_sha256": metrics["dataset_sha256"],
        "training_metrics_file": "metrics.json",
        "warning": (
            "Load only model.joblib files produced by a trusted local training "
            "run. Joblib/pickle model files must not be loaded from untrusted sources."
        ),
    }

    joblib.dump({"pipeline": model, "metadata": metadata}, model_path)

    test_output = df.iloc[test_idx][
        ["event_id", args.group_column, "timestamp"]
    ].copy()
    test_output["actual_label"] = y_test.to_numpy()
    test_output["predicted_label"] = predicted
    test_output["positive_class_score_not_calibrated"] = positive_scores
    test_output.to_csv(
        output_dir / "holdout_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )

    model_hash = sha256_file(model_path)
    metadata["model_sha256"] = model_hash
    (output_dir / "model_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "model.joblib.sha256").write_text(
        f"{model_hash}  model.joblib\n",
        encoding="ascii",
    )

    print(f"Training run: {output_dir}")
    print(f"Holdout precision: {metrics['precision']:.4f}")
    print(f"Holdout recall: {metrics['recall']:.4f}")
    print(f"Holdout average precision: {metrics['average_precision']:.4f}")
    print("These metrics are for the supplied dataset only.")
    return 0


def score(args) -> int:
    model_path = Path(args.model).expanduser().resolve(strict=True)
    bundle = joblib.load(model_path)  # Only load trusted locally trained models.
    if not isinstance(bundle, dict) or "pipeline" not in bundle:
        raise ValueError("Unexpected model bundle format.")

    metadata = bundle["metadata"]
    df, csv_path = load_events(
        args.input,
        group_column=metadata["group_column"],
        label_column=None,
    )

    x = df[metadata["feature_columns"]]
    predicted = bundle["pipeline"].predict(x).astype(int)
    classifier = bundle["pipeline"].named_steps["classifier"]
    classes = list(classifier.classes_)
    positive_index = classes.index(1)
    scores = bundle["pipeline"].predict_proba(x)[:, positive_index]

    output_dir = create_run_dir(args.output_root)
    output = df[["event_id", metadata["group_column"], "timestamp"]].copy()
    output["model_prediction"] = predicted
    output["positive_class_score_not_calibrated"] = scores
    output["interpretation"] = (
        "Triage output only; not a probability of wrongdoing or credibility."
    )
    output.to_csv(output_dir / "predictions.csv", index=False, encoding="utf-8-sig")

    result_meta = {
        "schema": "chronofact-phase6-score-run-v1",
        "created_at_utc": utc_now(),
        "model_path": str(model_path),
        "model_sha256": sha256_file(model_path),
        "input_path": str(csv_path),
        "input_sha256": sha256_file(csv_path),
        "row_count": len(output),
        "predictions_file": "predictions.csv",
        "warning": (
            "Scores are not calibrated probabilities. Human review and "
            "case-specific validation are required."
        ),
    }
    (output_dir / "score_manifest.json").write_text(
        json.dumps(result_meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Scoring output: {output_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train or score a grouped-holdout CHRONOFACT baseline model."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    train_parser = sub.add_parser("train")
    train_parser.add_argument("--input", required=True)
    train_parser.add_argument("--output-root", required=True)
    train_parser.add_argument("--group-column", default="scenario_id")
    train_parser.add_argument("--label-column", default="label")
    train_parser.add_argument(
        "--positive-label-definition",
        required=True,
        help="Human-readable description of what label 1 means.",
    )

    score_parser = sub.add_parser("score")
    score_parser.add_argument("--model", required=True)
    score_parser.add_argument("--input", required=True)
    score_parser.add_argument("--output-root", required=True)

    args = parser.parse_args()
    if args.command == "train":
        return train(args)
    return score(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Phase 6 failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)