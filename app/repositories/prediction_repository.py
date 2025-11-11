from __future__ import annotations

from typing import List, Type

from sqlalchemy.orm import Session

from app.entities.prediction import Prediction
from app.dtos.prediction_dto import PredictionInput


def create_prediction(
    db: Session,
    user_id: int,
    inp: PredictionInput,
    value: float,
) -> Prediction:
    prediction_record = Prediction(
        user_id=user_id,
        longitude=inp.longitude,
        latitude=inp.latitude,
        housing_median_age=inp.housing_median_age,
        total_rooms=inp.total_rooms,
        total_bedrooms=inp.total_bedrooms,
        population=inp.population,
        households=inp.households,
        median_income=inp.median_income,
        ocean_proximity=inp.ocean_proximity,
        prediction=value
    )
    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)
    return prediction_record


def list_predictions(db: Session, user_id: int | None = None) -> list[Type[Prediction]]:
    query = db.query(Prediction)
    if user_id is not None:
        query = query.filter(Prediction.user_id == user_id)
    return query.order_by(Prediction.id.desc()).all()
