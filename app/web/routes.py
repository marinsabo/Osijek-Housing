from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@router.get("/home")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html")