from fastapi import FastAPI, Depends
from app.web.routes import router
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.database import get_session

app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "web" / "static"), name="static")

@app.get("/health")
def root():
    return {"status": "ok"}

@app.get("/health/db")
def check(session = Depends(get_session)):
    return {"db": session.execute(text("SELECT 1")).scalar()}
