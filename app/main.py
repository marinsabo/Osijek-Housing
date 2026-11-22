from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"

print(TEMPLATES_DIR, TEMPLATES_DIR.exists(), flush=True)
print(STATIC_DIR, STATIC_DIR.exists(), flush=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app = FastAPI()

app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")