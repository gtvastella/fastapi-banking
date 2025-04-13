from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class PersonBase(BaseModel):
    name: str
    email: EmailStr
    address: str
    city: str
    state: str
    password: str
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres')
        return v

class NaturalPersonCreate(PersonBase):
    cpf: str
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v):
        if not re.match(r'^\d{11}$', v):
            raise ValueError('CPF deve conter 11 dígitos')
        return v

class LegalPersonCreate(PersonBase):
    cnpj: str
    
    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        if not re.match(r'^\d{14}$', v):
            raise ValueError('CNPJ deve conter 14 dígitos')
        return v

class PersonCreate(PersonBase):
    person_type: int = Field(..., description="1 para Pessoa Física, 2 para Pessoa Jurídica")
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v, info):
        person_type = info.data.get('person_type')
        if person_type == 1 and not v:
            raise ValueError('CPF é obrigatório para Pessoa Física')
        if v and not re.match(r'^\d{11}$', v):
            raise ValueError('CPF deve conter 11 dígitos')
        return v
    
    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v, info):
        person_type = info.data.get('person_type')
        if person_type == 2 and not v:
            raise ValueError('CNPJ é obrigatório para Pessoa Jurídica')
        if v and not re.match(r'^\d{14}$', v):
            raise ValueError('CNPJ deve conter 14 dígitos')
        return v

class PersonResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    city: str
    state: str
    created_at: datetime
    updated_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
