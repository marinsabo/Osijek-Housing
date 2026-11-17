from fastapi import FastAPI
from app.web.routes import router
from pathlib import Path
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "web" / "static"), name="static")

@app.get("/health")
def root():
    return {"status": "ok"}