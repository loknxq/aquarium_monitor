from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.aquarium import Aquarium, Parameter, AquariumParameter
from app.services.recommendations import INHABITANT_PARAMETERS

router = APIRouter(prefix="/aquariums", tags=["aquariums"])

def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

@router.get("/", response_class=HTMLResponse)
async def list_aquariums(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    aquariums = db.query(Aquarium).filter(Aquarium.user_id == user.id).all()
    return {"aquariums": aquariums}

@router.get("/create", response_class=HTMLResponse)
async def create_aquarium_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    parameters = db.query(Parameter).all()
    inhabitants = list(INHABITANT_PARAMETERS.keys())
    return {"parameters": parameters, "inhabitants": inhabitants}

@router.post("/create")
async def create_aquarium(request: Request, name: str = Form(...), inhabitants: str = Form(...), parameters: List[int] = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    aquarium = Aquarium(name=name, user_id=user.id, inhabitants=inhabitants)
    db.add(aquarium)
    db.flush()
    for param_id in parameters:
        db.add(AquariumParameter(aquarium_id=aquarium.id, parameter_id=param_id))
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/delete/{aquarium_id}")
async def delete_aquarium(aquarium_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    aquarium = db.query(Aquarium).filter(Aquarium.id == aquarium_id, Aquarium.user_id == user.id).first()
    if aquarium:
        db.delete(aquarium)
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/{aquarium_id}")
async def get_aquarium(aquarium_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    aquarium = db.query(Aquarium).filter(Aquarium.id == aquarium_id, Aquarium.user_id == user.id).first()
    if not aquarium:
        return RedirectResponse(url="/dashboard", status_code=303)
    return aquarium