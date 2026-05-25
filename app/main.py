from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from datetime import datetime, date
import json
import pandas as pd
import io
import os
from typing import List, Optional
from dotenv import load_dotenv

from app.database import engine, get_db, Base
from app.models.user import User
from app.models.aquarium import Aquarium, Parameter, AquariumParameter
from app.models.measurement import Measurement
from app.auth import create_user, authenticate_user, get_user_by_username, hash_password, verify_password
from app.services.recommendations import get_recommendations, INHABITANT_PARAMETERS

load_dotenv()

app = FastAPI(title="Aquarium Monitor API")

SECRET_KEY = os.getenv("SECRET_KEY", "mySecretKeyForAquariumApp2026")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 7
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

PARAMETERS_DB = [
    {"id": 1, "name": "temperature", "display_name": "Температура", "unit": "C"},
    {"id": 2, "name": "ph", "display_name": "pH", "unit": ""},
    {"id": 3, "name": "ammonia", "display_name": "Аммиак", "unit": "mg/L"},
    {"id": 4, "name": "nitrites", "display_name": "Нитриты", "unit": "mg/L"},
    {"id": 5, "name": "nitrates", "display_name": "Нитраты", "unit": "mg/L"},
    {"id": 6, "name": "gh", "display_name": "Жесткость GH", "unit": "dGH"},
    {"id": 7, "name": "kh", "display_name": "Жесткость KH", "unit": "dKH"},
    {"id": 8, "name": "co2", "display_name": "CO2", "unit": "mg/L"},
    {"id": 9, "name": "salinity", "display_name": "Соленость", "unit": "SG"},
    {"id": 10, "name": "calcium", "display_name": "Кальций", "unit": "mg/L"},
    {"id": 11, "name": "magnesium", "display_name": "Магний", "unit": "mg/L"},
    {"id": 12, "name": "phosphates", "display_name": "Фосфаты", "unit": "mg/L"}
]

async def init_parameters(db: AsyncSession):
    for param in PARAMETERS_DB:
        result = await db.execute(select(Parameter).where(Parameter.name == param["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            db.add(Parameter(name=param["name"], display_name=param["display_name"], unit=param["unit"]))
    await db.commit()

async def get_current_user(request: Request, db: AsyncSession):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async for db in get_db():
        await init_parameters(db)
        break

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.post("/api/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, username)
    if existing:
        return JSONResponse(status_code=400, content={"error": "Пользователь уже существует"})
    user = await create_user(db, username, password)
    request.session["user_id"] = user.id
    return JSONResponse(content={"success": True, "user_id": user.id, "username": user.username})

@app.post("/api/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, username, password)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Неверный логин или пароль"})
    request.session["user_id"] = user.id
    return JSONResponse(content={"success": True, "user_id": user.id, "username": user.username})

@app.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse(content={"success": True})

@app.get("/api/user")
async def get_user(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    return JSONResponse(content={"id": user.id, "username": user.username})

@app.get("/api/aquariums")
async def get_aquariums(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    result = await db.execute(select(Aquarium).where(Aquarium.user_id == user.id))
    aquariums = result.scalars().all()
    return JSONResponse(content=[{
        "id": a.id,
        "name": a.name,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "inhabitants": a.inhabitants,
        "photo": a.photo
    } for a in aquariums])

@app.post("/api/aquariums")
async def create_aquarium(request: Request, name: str = Form(...), inhabitants: str = Form(...), parameters: List[int] = Form(...), photo: str = Form(None), db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    if len(parameters) == 0:
        return JSONResponse(status_code=400, content={"error": "Выберите хотя бы один параметр"})
    aquarium = Aquarium(name=name, user_id=current_user.id, inhabitants=inhabitants, photo=photo if photo and photo.strip() else None)
    db.add(aquarium)
    await db.flush()
    for param_id in parameters:
        db.add(AquariumParameter(aquarium_id=aquarium.id, parameter_id=param_id))
    await db.commit()
    return JSONResponse(content={"id": aquarium.id, "name": aquarium.name})

@app.delete("/api/aquariums/{aquarium_id}")
async def delete_aquarium(aquarium_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    await db.execute(delete(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    await db.commit()
    return JSONResponse(content={"success": True})

@app.get("/api/aquariums/{aquarium_id}")
async def get_aquarium(aquarium_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return JSONResponse(status_code=404, content={"error": "Aquarium not found"})
    
    result_params = await db.execute(select(AquariumParameter).where(AquariumParameter.aquarium_id == aquarium_id))
    aquarium_params = result_params.scalars().all()
    param_ids = [ap.parameter_id for ap in aquarium_params]
    result_params_list = await db.execute(select(Parameter).where(Parameter.id.in_(param_ids)))
    parameters = result_params_list.scalars().all()
    
    return JSONResponse(content={
        "id": aquarium.id,
        "name": aquarium.name,
        "inhabitants": aquarium.inhabitants,
        "photo": aquarium.photo,
        "parameters": [{"id": p.id, "name": p.name, "display_name": p.display_name, "unit": p.unit} for p in parameters]
    })

@app.post("/api/aquariums/{aquarium_id}/measurements")
async def add_measurement(request: Request, aquarium_id: int, date_str: str = Form(...), values: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return JSONResponse(status_code=404, content={"error": "Aquarium not found"})
    try:
        measurement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        measurement_date = date.today()
    values_dict = json.loads(values)
    for param_name, value in values_dict.items():
        param_result = await db.execute(select(Parameter).where(Parameter.name == param_name))
        param = param_result.scalar_one_or_none()
        if param:
            existing_result = await db.execute(select(Measurement).where(
                Measurement.aquarium_id == aquarium_id,
                Measurement.parameter_id == param.id,
                Measurement.date == measurement_date
            ))
            existing = existing_result.scalar_one_or_none()
            if existing:
                existing.value = value
            else:
                db.add(Measurement(
                    aquarium_id=aquarium_id,
                    parameter_id=param.id,
                    date=measurement_date,
                    value=value
                ))
    await db.commit()
    return JSONResponse(content={"success": True})

@app.get("/api/aquariums/{aquarium_id}/measurements")
async def get_measurements(aquarium_id: int, start_date: str = None, end_date: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Measurement).where(Measurement.aquarium_id == aquarium_id)
    if start_date:
        query = query.where(Measurement.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
    if end_date:
        query = query.where(Measurement.date <= datetime.strptime(end_date, "%Y-%m-%d").date())
    query = query.order_by(Measurement.date)
    result = await db.execute(query)
    measurements = result.scalars().all()
    result_list = []
    for m in measurements:
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        result_list.append({
            "id": m.id,
            "date": m.date.strftime("%Y-%m-%d"),
            "parameter": param.name if param else "unknown",
            "parameter_display": param.display_name if param else "Unknown",
            "value": float(m.value),
            "unit": param.unit if param else ""
        })
    return JSONResponse(content=result_list)

@app.get("/api/aquariums/{aquarium_id}/measurements_pivot")
async def get_measurements_pivot(aquarium_id: int, start_date: str = None, end_date: str = None, parameters: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Measurement).where(Measurement.aquarium_id == aquarium_id)
    if start_date:
        query = query.where(Measurement.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
    if end_date:
        query = query.where(Measurement.date <= datetime.strptime(end_date, "%Y-%m-%d").date())
    query = query.order_by(Measurement.date)
    result = await db.execute(query)
    measurements = result.scalars().all()
    
    result_params = await db.execute(select(AquariumParameter).where(AquariumParameter.aquarium_id == aquarium_id))
    aquarium_params = result_params.scalars().all()
    param_ids = [ap.parameter_id for ap in aquarium_params]
    params_list = await db.execute(select(Parameter).where(Parameter.id.in_(param_ids)))
    parameters_list = params_list.scalars().all()
    
    filter_param_names = None
    if parameters:
        filter_param_names = set(parameters.split(','))
    
    pivot_data = {}
    for m in measurements:
        date_str = m.date.strftime("%Y-%m-%d")
        if date_str not in pivot_data:
            pivot_data[date_str] = {"date": date_str}
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        if param and (not filter_param_names or param.name in filter_param_names):
            pivot_data[date_str][param.name] = float(m.value)
    
    display_parameters = [p for p in parameters_list if not filter_param_names or p.name in filter_param_names]
    
    for param in display_parameters:
        for date_str in pivot_data:
            if param.name not in pivot_data[date_str]:
                pivot_data[date_str][param.name] = None
    
    result_list = sorted(pivot_data.values(), key=lambda x: x["date"])
    
    return JSONResponse(content={
        "data": result_list,
        "parameters": [{"name": p.name, "display_name": p.display_name, "unit": p.unit} for p in display_parameters]
    })

@app.get("/api/parameters")
async def get_parameters_api(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Parameter))
    params = result.scalars().all()
    return JSONResponse(content=[{"id": p.id, "name": p.name, "display_name": p.display_name, "unit": p.unit} for p in params])

@app.get("/api/recommendations/{aquarium_id}")
async def get_recommendations_api(aquarium_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return JSONResponse(content={"recommendations": [], "has_issues": False})
    result_meas = await db.execute(select(Measurement).where(Measurement.aquarium_id == aquarium_id).order_by(desc(Measurement.date)).limit(20))
    latest_measurements = result_meas.scalars().all()
    measurements_by_param = {}
    for m in latest_measurements:
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        if param and param.name not in measurements_by_param:
            measurements_by_param[param.name] = float(m.value)
    recs = get_recommendations(aquarium.inhabitants, measurements_by_param)
    return JSONResponse(content={"recommendations": recs, "has_issues": len(recs) > 0})

@app.get("/api/aquariums/{aquarium_id}/export")
async def export_csv(aquarium_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return JSONResponse(status_code=404, content={"error": "Aquarium not found"})
    result_meas = await db.execute(select(Measurement).where(Measurement.aquarium_id == aquarium_id).order_by(Measurement.date))
    measurements = result_meas.scalars().all()
    data = []
    for m in measurements:
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        data.append({
            "Дата": m.date.strftime("%Y-%m-%d"),
            "Параметр": param.display_name if param else "Unknown",
            "Значение": float(m.value),
            "Единица измерения": param.unit if param else ""
        })
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)
    return StreamingResponse(iter([output.getvalue().encode("utf-8-sig")]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=aquarium_{aquarium_id}_export.csv"})

@app.post("/api/profile/change-password")
async def change_password(request: Request, old_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    
    if new_password != confirm_password:
        return JSONResponse(status_code=400, content={"error": "Новые пароли не совпадают"})
    
    if not verify_password(old_password, user.password_hash):
        return JSONResponse(status_code=400, content={"error": "Неверный текущий пароль"})
    
    user.password_hash = hash_password(new_password)
    await db.commit()
    
    return JSONResponse(content={"success": True})