from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from datetime import datetime, date, timedelta
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
from app.auth_jwt import (
    create_access_token, decode_token, get_token_from_request,
    get_current_user_from_token, create_user, authenticate_user,
    get_user_by_username, hash_password, verify_password
)
from app.services.recommendations import get_recommendations, INHABITANT_PARAMETERS

load_dotenv()

app = FastAPI(title="Aquarium Monitor")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

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
    return await get_current_user_from_token(request, db)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async for db in get_db():
        await init_parameters(db)
        break

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, username)
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
    user = await create_user(db, username, password)
    access_token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60*60*24*30,
        samesite="lax"
    )
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})
    access_token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60*60*24*30,
        samesite="lax"
    )
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    result = await db.execute(select(Aquarium).where(Aquarium.user_id == user.id))
    aquariums = result.scalars().all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "aquariums": aquariums, "user": user})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/profile/change-password")
async def change_password(request: Request, old_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    if new_password != confirm_password:
        return templates.TemplateResponse("profile.html", {"request": request, "user": user, "error": "Новые пароли не совпадают"})
    
    if not verify_password(old_password, user.password_hash):
        return templates.TemplateResponse("profile.html", {"request": request, "user": user, "error": "Неверный текущий пароль"})
    
    user.password_hash = hash_password(new_password)
    await db.commit()
    
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "success": "Пароль успешно изменен"})

@app.get("/aquarium/create", response_class=HTMLResponse)
async def create_aquarium_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    result = await db.execute(select(Parameter))
    parameters = result.scalars().all()
    inhabitants = list(INHABITANT_PARAMETERS.keys())
    return templates.TemplateResponse("aquarium_create.html", {"request": request, "parameters": parameters, "inhabitants": inhabitants})

@app.post("/aquarium/create")
async def create_aquarium(request: Request, name: str = Form(...), inhabitants: str = Form(...), parameters: List[int] = Form(...), photo: str = Form(None), db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    if len(parameters) == 0:
        result = await db.execute(select(Parameter))
        params = result.scalars().all()
        inhabitants_list = list(INHABITANT_PARAMETERS.keys())
        return templates.TemplateResponse("aquarium_create.html", {"request": request, "error": "Выберите хотя бы один параметр", "parameters": params, "inhabitants": inhabitants_list})
    aquarium = Aquarium(name=name, user_id=current_user.id, inhabitants=inhabitants, photo=photo if photo and photo.strip() else None)
    db.add(aquarium)
    await db.flush()
    for param_id in parameters:
        db.add(AquariumParameter(aquarium_id=aquarium.id, parameter_id=param_id))
    await db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/aquarium/delete/{aquarium_id}")
async def delete_aquarium(aquarium_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    await db.execute(delete(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    await db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/aquarium/{aquarium_id}", response_class=HTMLResponse)
async def aquarium_detail(request: Request, aquarium_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return RedirectResponse(url="/dashboard", status_code=303)
    result_params = await db.execute(select(AquariumParameter).where(AquariumParameter.aquarium_id == aquarium_id))
    aquarium_params = result_params.scalars().all()
    param_ids = [ap.parameter_id for ap in aquarium_params]
    result_params_list = await db.execute(select(Parameter).where(Parameter.id.in_(param_ids)))
    parameters = result_params_list.scalars().all()
    param_dict = {p.name: {"id": p.id, "display_name": p.display_name, "unit": p.unit} for p in parameters}
    result_measurements = await db.execute(select(Measurement).where(Measurement.aquarium_id == aquarium_id).order_by(desc(Measurement.date)).limit(50))
    measurements = result_measurements.scalars().all()
    measurements_data = []
    for m in measurements:
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        measurements_data.append({
            "id": m.id,
            "date": m.date.strftime("%Y-%m-%d"),
            "parameter_name": param.name if param else "unknown",
            "parameter_display": param.display_name if param else "Unknown",
            "value": float(m.value),
            "unit": param.unit if param else ""
        })
    return templates.TemplateResponse("aquarium_detail.html", {
        "request": request,
        "aquarium": aquarium,
        "parameters": parameters,
        "measurements": measurements_data,
        "param_dict": param_dict
    })

@app.post("/aquarium/{aquarium_id}/measurement")
async def add_measurement(request: Request, aquarium_id: int, date_str: str = Form(...), values: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return RedirectResponse(url="/dashboard", status_code=303)
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
    return RedirectResponse(url=f"/aquarium/{aquarium_id}", status_code=303)

@app.get("/api/measurements/{aquarium_id}")
async def get_measurements_api(aquarium_id: int, start_date: str = None, end_date: str = None, db: AsyncSession = Depends(get_db)):
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
            "date": m.date.strftime("%Y-%m-%d"),
            "parameter": param.name if param else "unknown",
            "value": float(m.value)
        })
    return result_list

@app.get("/api/measurements_pivot/{aquarium_id}")
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
    
    return {"data": result_list, "parameters": [{"name": p.name, "display_name": p.display_name, "unit": p.unit} for p in display_parameters]}

@app.get("/api/parameters")
async def get_parameters_api(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Parameter))
    params = result.scalars().all()
    return [{"id": p.id, "name": p.name, "display_name": p.display_name, "unit": p.unit} for p in params]

@app.get("/api/recommendations/{aquarium_id}")
async def get_recommendations_api(aquarium_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return {"recommendations": []}
    result_meas = await db.execute(select(Measurement).where(Measurement.aquarium_id == aquarium_id).order_by(desc(Measurement.date)).limit(20))
    latest_measurements = result_meas.scalars().all()
    measurements_by_param = {}
    for m in latest_measurements:
        param_result = await db.execute(select(Parameter).where(Parameter.id == m.parameter_id))
        param = param_result.scalar_one_or_none()
        if param and param.name not in measurements_by_param:
            measurements_by_param[param.name] = float(m.value)
    recs = get_recommendations(aquarium.inhabitants, measurements_by_param)
    return {"recommendations": recs, "has_issues": len(recs) > 0}

@app.get("/aquarium/{aquarium_id}/export")
async def export_csv(aquarium_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    result = await db.execute(select(Aquarium).where(Aquarium.id == aquarium_id, Aquarium.user_id == user.id))
    aquarium = result.scalar_one_or_none()
    if not aquarium:
        return RedirectResponse(url="/dashboard", status_code=303)
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

@app.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response