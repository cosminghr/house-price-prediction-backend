from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.dtos.prediction_dto import PredictionInput, PredictionOutput, PredictionRead
from app.services.prediction_service import predict_and_store
from app.repositories.prediction_repository import list_predictions
from app.controllers.auth_controller import get_current_user
from app.entities.user import User

router = APIRouter(prefix="/predict", tags=["predict"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=PredictionOutput)
def make_prediction(
        data: PredictionInput,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    y, pred_id = predict_and_store(db, current_user.id, data)
    return {"prediction": y, "prediction_id": pred_id}


@router.get("", response_model=list[PredictionRead])
def my_predictions(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return list_predictions(db, user_id=current_user.id)
