from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    housing_median_age = Column(Float, nullable=False)
    total_rooms = Column(Float, nullable=False)
    total_bedrooms = Column(Float, nullable=False)
    population = Column(Float, nullable=False)
    households = Column(Float, nullable=False)
    median_income = Column(Float, nullable=False)
    ocean_proximity = Column(String, nullable=False)

    prediction = Column(Float, nullable=False)

    user = relationship("User", backref="predictions")
