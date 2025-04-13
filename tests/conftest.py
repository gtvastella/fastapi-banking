import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base, get_db
from app.main import app
from app.models.person import Person, TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON
from app.core.security import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    app.middleware_stack = app.build_middleware_stack()
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_natural_person(db_session):
    hashed_password = get_password_hash("senha123")
    person = Person(
        name="João Silva",
        email="joao@example.com",
        password=hashed_password,
        address="Rua Teste, 123",
        city="São Paulo",
        state="SP",
        cpf="12345678901",
        balance=1000.0,
        type=TYPE_NATURAL_PERSON
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture(scope="function")
def test_legal_person(db_session):
    hashed_password = get_password_hash("senha123")
    person = Person(
        name="Empresa Teste LTDA",
        email="empresa@example.com",
        password=hashed_password,
        address="Av Comercial, 456",
        city="São Paulo",
        state="SP",
        cnpj="12345678901234",
        balance=5000,
        type=TYPE_LEGAL_PERSON
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture(scope="function")
def client_with_auth(client, test_natural_person, monkeypatch):
    from app.core.auth_middleware import AuthMiddleware
    
    def create_auth_client(person):
        access_token = create_access_token(data={"sub": str(person.id)})
        
        def mock_verify_token(self, token, *args, **kwargs):
            return person
        
        monkeypatch.setattr(AuthMiddleware, "_verify_token", mock_verify_token)
        
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        return client
        
    return create_auth_client


@pytest.fixture(scope="function")
def client_natural_person(client_with_auth, test_natural_person):
    return client_with_auth(test_natural_person)


@pytest.fixture(scope="function")
def client_legal_person(client_with_auth, test_legal_person):
    return client_with_auth(test_legal_person)


