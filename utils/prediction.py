
import os
import joblib
import pandas as pd
import numpy as np


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "model",
    "voice_sense_random_forest.pkl"
)


def load_model():
    """Load the trained Random Forest model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_voice(features, model=None):
    """
    Predict from a dictionary containing the 37 extracted features.

    Returns the predicted label, both class probabilities,
    and the model's maximum class probability.
    """

    if model is None:
        model = load_model()

    # Preserve the feature order expected by the trained model.
    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        raise ValueError(
            "Model does not contain feature names. "
            "Provide the training feature order before predicting."
        )

    missing = [
        name for name in feature_names
        if name not in features
    ]

    if missing:
        raise ValueError(
            f"Missing required features: {missing}"
        )

    # Construct input using the exact model feature order.
    X = pd.DataFrame(
        [[features[name] for name in feature_names]],
        columns=feature_names
    )

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError(
            "Features contain invalid numeric values."
        )

    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]

    class_probabilities = {
        int(class_label): float(probability)
        for class_label, probability
        in zip(model.classes_, probabilities)
    }

    labels = {
        0: "Healthy",
        1: "Parkinsons"
    }

    return {
        "prediction": prediction,
        "label": labels.get(prediction, str(prediction)),
        "confidence": max(class_probabilities.values()) * 100,
        "healthy_probability": class_probabilities.get(0, 0.0) * 100,
        "parkinson_probability": class_probabilities.get(1, 0.0) * 100
    }
