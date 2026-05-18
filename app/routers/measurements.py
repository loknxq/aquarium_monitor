from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, date
import json
from app.database import get_db
from app.models.user import User
from app.models.aquarium import Aquarium, Parameter
from app.models.measurement import Measurement

router = APIRouter(prefix="/measurements", tags=["measurements"])

def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

@router.post("/add/{aquarium_id}")
async def add_measurement(request: Request, aquarium_id: int, date_str: str = Form(...), values: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    aquarium = db.query(Aquarium).filter(Aquarium.id == aquarium_id, Aquarium.user_id == user.id).first()
    if not aquarium:
        return RedirectResponse(url="/dashboard", status_code=303)
    try:
        measurement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        measurement_date = date.today()
    values_dict = json.loads(values)
    for param_name, value in values_dict.items():
        param = db.query(Parameter).filter(Parameter.name == param_name).first()
        if param:
            existing = db.query(Measurement).filter(
                Measurement.aquarium_id == aquarium_id,
                Measurement.parameter_id == param.id,
                Measurement.date == measurement_date
            ).first()
            if existing:
                existing.value = value
            else:
                db.add(Measurement(
                    aquarium_id=aquarium_id,
                    parameter_id=param.id,
                    date=measurement_date,
                    value=value
                ))
    db.commit()
    return RedirectResponse(url=f"/aquarium/{aquarium_id}", status_code=303)

@router.get("/history/{aquarium_id}")
async def get_measurements(aquarium_id: int, start_date: str = None, end_date: str = None, request: Request = None, db: Session = Depends(get_db)):
    query = db.query(Measurement).filter(Measurement.aquarium_id == aquarium_id)
    if start_date:
        query = query.filter(Measurement.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
    if end_date:
        query = query.filter(Measurement.date <= datetime.strptime(end_date, "%Y-%m-%d").date())
    measurements = query.order_by(Measurement.date).all()
    result = []
    for m in measurements:
        param = db.query(Parameter).filter(Parameter.id == m.parameter_id).first()
        result.append({
            "date": m.date.strftime("%Y-%m-%d"),
            "parameter": param.name if param else "unknown",
            "value": float(m.value)
        })
    return result