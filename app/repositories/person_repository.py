from sqlalchemy.orm import Session
from app.models.person import Person, TYPE_LEGAL_PERSON, TYPE_NATURAL_PERSON
from app.core.security import get_password_hash
from datetime import datetime, timezone
from app.repositories.base_repository import BaseRepository

class PersonRepository(BaseRepository[Person]):
    def __init__(self, db: Session):
        super().__init__(db, Person)

    def get_by_email(self, email: str):
        return self.get_one_by(email=email)
    
    def get_by_id(self, user_id: int):
        return self.db.query(Person).filter(Person.id == user_id).first()
    
    def get_natural_person_by_id(self, user_id: int):
        return self.db.query(Person).filter(Person.id == user_id, Person.type == TYPE_NATURAL_PERSON).first()
    
    def get_legal_person_by_id(self, user_id: int):
        return self.db.query(Person).filter(Person.id == user_id, Person.type == TYPE_LEGAL_PERSON).first()
    
    def create_natural_person(self, name: str, email: str, password: str, address: str, city: str, state: str, cpf: str):
        hashed_password = get_password_hash(password)
        return self.create(
            name=name,
            email=email,
            password=hashed_password,
            address=address,
            city=city,
            state=state,
            cpf=cpf,
            type=TYPE_NATURAL_PERSON
        )
    
    def create_legal_person(self, name: str, email: str, password: str, address: str, city: str, state: str, cnpj: str):
        hashed_password = get_password_hash(password)
        return self.create(
            name=name,
            email=email,
            password=hashed_password,
            address=address,
            city=city,
            state=state,
            cnpj=cnpj,
            type=TYPE_LEGAL_PERSON
        )
    
    def update_last_login(self, user_id: int):
        return self.update(user_id, last_login=datetime.now(timezone.utc))
    
    def update_balance(self, user_id: int, amount: float):
        user = self.get_by_id(user_id)
        if user:
            user.balance += amount
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
