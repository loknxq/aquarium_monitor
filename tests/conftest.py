import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
import os
from dotenv import load_dotenv

from app.main import app
from app.database import Base, get_db

load_dotenv()

DATABASE_URL = "postgresql+asyncpg://postgres:020306@localhost:5433/aquarium_test_db"

engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(setup_database):
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
async def test_user(db_session):
    from app.auth import hash_password
    from app.models.user import User
    
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
async def test_parameters(db_session):
    from app.models.aquarium import Parameter
    
    params = [
        Parameter(name="temperature", display_name="Температура", unit="C"),
        Parameter(name="ph", display_name="pH", unit=""),
        Parameter(name="ammonia", display_name="Аммиак", unit="mg/L"),
        Parameter(name="nitrites", display_name="Нитриты", unit="mg/L"),
    ]
    for param in params:
        db_session.add(param)
    await db_session.commit()
    for param in params:
        await db_session.refresh(param)
    return params

@pytest.fixture(scope="function")
async def test_aquarium(db_session, test_user, test_parameters):
    from app.models.aquarium import Aquarium, AquariumParameter
    
    aquarium = Aquarium(
        name="Test Aquarium",
        user_id=test_user.id,
        inhabitants="tropical_fish"
    )
    db_session.add(aquarium)
    await db_session.commit()
    await db_session.refresh(aquarium)
    
    for param in test_parameters:
        db_session.add(AquariumParameter(aquarium_id=aquarium.id, parameter_id=param.id))
    await db_session.commit()
    
    return aquarium