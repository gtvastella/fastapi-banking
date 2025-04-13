from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.v1.routes import auth_router, transaction_router
from app.core.database import create_tables
from app.core.auth_middleware import AuthMiddleware
from app.core.exceptions import AppException
from contextlib import asynccontextmanager
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    python_exception_handler,
    pydantic_validation_exception_handler
)
import typer
import alembic.config
import alembic.command

cli = typer.Typer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Banking API",
    description="API for banking operations including transfers, deposits and withdrawals",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)

app.include_router(auth_router.router, prefix="/api/v1", tags=["auth"])
app.include_router(transaction_router.router, prefix="/api/v1", tags=["transactions"])

@app.get("/")
def read_root():
    return {"message": "Banking API is running"}

@cli.command()
def makemigrations(message: str = "auto-generated migration"):
    try:
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.revision(alembic_cfg, autogenerate=True, message=message)
        typer.echo("✅ Migration files created successfully!")
    except Exception as e:
        typer.echo(f"❌ Error generating migrations: {str(e)}")
        raise typer.Exit(code=1)

@cli.command()
def migrate(revision: str = "head"):
    try:
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.upgrade(alembic_cfg, revision)
        typer.echo(f"✅ Database migrated successfully to {revision}!")
    except Exception as e:
        typer.echo(f"❌ Error applying migrations: {str(e)}")
        raise typer.Exit(code=1)

@cli.command()
def downgrade(revision: str = "-1"):
    try:
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.downgrade(alembic_cfg, revision)
        typer.echo(f"✅ Database downgraded successfully to {revision}!")
    except Exception as e:
        typer.echo(f"❌ Error downgrading database: {str(e)}")
        raise typer.Exit(code=1)

@cli.command()
def show_migrations():
    try:
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.history(alembic_cfg)
        typer.echo("\n✅ Current migration status:")
        alembic.command.current(alembic_cfg, verbose=True)
    except Exception as e:
        typer.echo(f"❌ Error showing migrations: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    cli()
