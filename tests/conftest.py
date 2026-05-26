# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.aquarium import Aquarium, Parameter, AquariumParameter
from app.models.measurement import Measurement
from app.auth import hash_password


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:020306@localhost:5433/aquarium_test"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

AsyncTestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def setup_database():
    """Создание таблиц один раз перед всеми тестами"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД для тестов"""
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_db(db_session: AsyncSession):
    """Очистка всех таблиц перед каждым тестом"""
    # Удаляем данные в правильном порядке (сначала дочерние таблицы)
    await db_session.execute(text("TRUNCATE TABLE measurements RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE aquarium_parameters RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE aquariums RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE parameters RESTART IDENTITY CASCADE"))
    await db_session.commit()
    yield


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для тестирования API"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Создание тестового пользователя"""
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user2(db_session: AsyncSession):
    """Второй тестовый пользователь"""
    user = User(
        username="testuser2",
        password_hash=hash_password("testpass456"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_parameters(db_session: AsyncSession):
    """Создание тестовых параметров"""
    params = [
        Parameter(name="temperature", display_name="Температура", unit="C"),
        Parameter(name="ph", display_name="pH", unit=""),
        Parameter(name="ammonia", display_name="Аммиак", unit="mg/L"),
        Parameter(name="nitrites", display_name="Нитриты", unit="mg/L"),
        Parameter(name="nitrates", display_name="Нитраты", unit="mg/L"),
    ]
    for param in params:
        db_session.add(param)
    await db_session.commit()
    
    return params


@pytest.fixture
async def test_aquarium(db_session: AsyncSession, test_user: User):
    """Создание тестового аквариума"""
    aquarium = Aquarium(
        name="Test Aquarium",
        user_id=test_user.id,
        inhabitants="tropical_fish"
    )
    db_session.add(aquarium)
    await db_session.commit()
    await db_session.refresh(aquarium)
    return aquarium


@pytest.fixture
async def test_aquarium_with_params(
    db_session: AsyncSession, 
    test_aquarium: Aquarium, 
    test_parameters: list
):
    """Аквариум с привязанными параметрами"""
    for param in test_parameters:
        aquarium_param = AquariumParameter(
            aquarium_id=test_aquarium.id,
            parameter_id=param.id
        )
        db_session.add(aquarium_param)
    await db_session.commit()
    return test_aquarium


@pytest.fixture
async def authenticated_client(client: AsyncClient, db_session: AsyncSession):
    """Авторизованный клиент"""
    # Создаем пользователя
    user = User(
        username="authuser",
        password_hash=hash_password("authpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Логинимся
    response = await client.post(
        "/api/login",
        data={"username": "authuser", "password": "authpass123"}
    )
    assert response.status_code == 200
    return client