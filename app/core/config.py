import os

SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "banking")