import joblib
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dtos.prediction_dto import PredictionInput
from app.repositories.prediction_repository import create_prediction

_model = None

MODEL_PATH = Path(settings.MODEL_PATH or "model.joblib")


OCEAN_CATEGORIES = [
    '<1H OCEAN',
    'INLAND',
    'ISLAND',
    'NEAR BAY',
    'NEAR OCEAN'
]


def load_model():

    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def encode_ocean_proximity(category: str):
    return [1 if category == c else 0 for c in OCEAN_CATEGORIES]


def build_feature_vector(data: PredictionInput):
    return [
        data.longitude,
        data.latitude,
        data.housing_median_age,
        data.total_rooms,
        data.total_bedrooms,
        data.population,
        data.households,
        data.median_income,
        *encode_ocean_proximity(data.ocean_proximity),
    ]


def predict_and_store(db: Session, user_id: int, data: PredictionInput):
    model = load_model()

    feature_vector = build_feature_vector(data)
    prediction_value = float(model.predict([feature_vector])[0])

    record = create_prediction(db, user_id=user_id, inp=data, value=prediction_value)

    return prediction_value, record.id
