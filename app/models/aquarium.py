from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Aquarium(Base):
    __tablename__ = "aquariums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    photo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    inhabitants = Column(String(200))
    
    user = relationship("User", backref="aquariums")
    measurements = relationship("Measurement", back_populates="aquarium", cascade="all, delete-orphan")
    parameters = relationship("AquariumParameter", back_populates="aquarium", cascade="all, delete-orphan")

class Parameter(Base):
    __tablename__ = "parameters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)

class AquariumParameter(Base):
    __tablename__ = "aquarium_parameters"

    id = Column(Integer, primary_key=True, index=True)
    aquarium_id = Column(Integer, ForeignKey("aquariums.id", ondelete="CASCADE"), nullable=False)
    parameter_id = Column(Integer, ForeignKey("parameters.id", ondelete="CASCADE"), nullable=False)
    
    aquarium = relationship("Aquarium", back_populates="parameters")
    parameter = relationship("Parameter")