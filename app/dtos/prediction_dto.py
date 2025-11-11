from pydantic import BaseModel, Field
from typing import Literal


class PredictionInput(BaseModel):
    longitude: float
    latitude: float
    housing_median_age: float = Field(..., ge=0)
    total_rooms: float = Field(..., ge=0)
    total_bedrooms: float = Field(..., ge=0)
    population: float = Field(..., ge=0)
    households: float = Field(..., ge=0)
    median_income: float = Field(..., ge=0)
    ocean_proximity: Literal['NEAR BAY', '<1H OCEAN', 'INLAND', 'NEAR OCEAN', 'ISLAND']


class PredictionRead(BaseModel):
    id: int
    user_id: int
    prediction: float

    class Config:
        from_attributes = True


class PredictionOutput(BaseModel):
    prediction: float
    prediction_id: int
